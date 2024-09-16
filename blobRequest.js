const axios = require('axios');
const fs = require('fs');
const csv = require('csv-parser');
const { parse } = require('json2csv');
require('dotenv').config();


const apiKey = process.env.API_KEY;
const startBlock = 19671560; // Replace with your start block number // First around 19500000 
const endBlock = 20651993; // Replace with your end block number
const batchSize = 4; // Adjust batch size based on performance testing
const delayBetweenRequestsMs = 1200; // 1.2 seconds delay between batches
const csvFilePath = 'block_data.csv';

async function getBlockByNumber(blockNumber, apiKey) {
    const url = `https://api.etherscan.io/api`;
    const params = {
        module: 'proxy',
        action: 'eth_getBlockByNumber',
        tag: `0x${blockNumber.toString(16)}`,
        boolean: 'true',
        apikey: apiKey
    };

    try {
        const response = await axios.get(url, { params });
        return response.data.result;
    } catch (error) {
        console.error(`Error fetching block ${blockNumber}: ${error.message}`);
        return null;
    }
}

function extractBlobCarryingTransactionLengths(block) {
    if (!block || !block.transactions) return [];

    return block.transactions
        .filter(tx => tx.type === '0x3')
        .map(tx => tx.blobVersionedHashes ? tx.blobVersionedHashes.length : 0);
}

function readExistingCsv(filePath) {
    return new Promise((resolve, reject) => {
        const existingBlocks = new Set();
        if (fs.existsSync(filePath)) {
            fs.createReadStream(filePath)
                .pipe(csv())
                .on('data', (row) => {
                    existingBlocks.add(parseInt(row.BlockNumber, 10));
                })
                .on('end', () => {
                    resolve(existingBlocks);
                })
                .on('error', reject);
        } else {
            resolve(existingBlocks);
        }
    });
}

async function sweepBlocks(startBlock, endBlock, apiKey, existingBlocks) {
    const blocksToFetch = [];
    for (let blockNumber = startBlock; blockNumber <= endBlock; blockNumber++) {
        if (!existingBlocks.has(blockNumber)) {
            blocksToFetch.push(blockNumber);
        }
    }

    if (blocksToFetch.length === 0) {
        console.log('All requested blocks are already in the CSV file.');
        return;
    }

    const csvStream = fs.createWriteStream(csvFilePath, { flags: 'a' });

    for (let i = 0; i < blocksToFetch.length; i += batchSize) {
        const batchPromises = blocksToFetch.slice(i, i + batchSize).map(blockNumber => getBlockByNumber(blockNumber, apiKey));

        try {
            const batchResults = await Promise.all(batchPromises);
            const rowsToAppend = [];
            batchResults.forEach(block => {
                if (block && block.number !== null && block.number !== undefined) {
                    const blockNumber = parseInt(block.number, 16);
                    if (!isNaN(blockNumber)) {
                        const lengths = extractBlobCarryingTransactionLengths(block);
                        const lengthsString = lengths.length > 0 ? lengths.join(', ') : '0';
                        console.log(`${blockNumber}: [${lengthsString}]`);
                        rowsToAppend.push({ BlockNumber: blockNumber, BlobLengths: lengthsString });
                    } else {
                        console.warn(`Invalid block number received: ${block.number}`);
                    }
                } else {
                    console.warn(`Invalid block data received: ${JSON.stringify(block)}`);
                }
            });

            if (rowsToAppend.length > 0) {
                const csvData = parse(rowsToAppend, { header: false });
                csvStream.write(`${csvData}\n`);
            }
        } catch (error) {
            console.error(`Error in fetching blocks: ${error.message}`);
        }

        // Introduce delay between batches to adhere to rate limits
        await new Promise(resolve => setTimeout(resolve, delayBetweenRequestsMs));
    }

    csvStream.end();
}

async function main() {
    const existingBlocks = await readExistingCsv(csvFilePath);
    await sweepBlocks(startBlock, endBlock, apiKey, existingBlocks);
}

main();
