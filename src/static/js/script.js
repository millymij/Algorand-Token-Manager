$(document).ready(function() {
    $('#send-transaction').click(function() {
        $('#dynamic-content').empty();
        $('#dynamic-content').html(`
        <div>
            <p>To facilitate the transfer of tokens via SMS, please follow the step-by-step procedure outlined below:</p>
            <ol>
                <li><strong>Upload TEAL Contract:</strong> Start by uploading your smart contract in TEAL format. This contract defines the logic and rules for the token transaction.</li>
                <li><strong>Generate Logic Signature:</strong> Once the contract is uploaded, click on 'Generate Logic Signature' to compile your contract and create a logic signature based on it. 
                <br>This is a first step to ensuring that the transaction adheres to the logic defined in the script.</li>
                <li><strong>Sign the Logic Signature:</strong> Sign the generated logic signature using your private key. This step ensures that the transaction is securely authorized by the sender.</li>
                <li><strong>Encode Logic Signature:</strong> The logic signature will then be encoded and displayed in the designated field. Encoding is necessary to make the signature sendable and readable via SMS.</li>
                <li><strong>Enter Receiver's Phone Number:</strong> Specify the phone number of the recipient who will receive the encoded logic signature via SMS. Ensure the correctness of the phone number to avoid sending sensitive information to the wrong recipient.</li>
                Upon successful sending, a message of success will appear in the text area below.
            </ol>
        </div>
        <h2>Create Token</h2>
        <div>
          <form id="teal-form" action="/upload" method="post" enctype="multipart/form-data">
            <label for="file-upload" class="label">1) Upload TEAL contract</label><br>
            <p>Begin by uploading the .teal contract detailing your logic signature's usage conditions.</p>
            <input type="file" id="file-upload" name="file"><br>
            <input type="hidden" id="amount-hidden" value=""/>
            <button type="submit">Upload</button>
            <div id="notification-teal"></div>
          </form>
          
        </div>
        <div>
            <label for="generate-lsig" class="label">2) Generate Logic Signature</label><br>
            <p>Generate a "Logic Signature Object" by compiling the contract.</p>
            <input type="button" id="generate-lsig" value="Generate Logic Signature" onclick="generateLogicSignature()">
            <div id="notification"></div>
        </div>

        <div>
            <form id="fetch-form-s-sender" action="javascript:void(0);">
                    <label for="s-address-input" class="label">3) Sender's Account Address</label><br>
                    <p>Please input your account's address, such that the redeemer will execute the transaction from that account.
                    <br>In case you don't have an account already, you can generate one.
                     </p>
                    <input type="text" id="s-address-input" name="s-address-input" placeholder="Enter Sender's Account Address Here">
                    <input type="submit" value="Fetch Account Info">
                  
            </form>
            <div>
                    <textarea id="s-output" readonly></textarea>
                    <button id="generate-account" style="margin-right: 10px;">Generate New Account</button>
                    <button id="clear-ss-address-input" style="margin-right: 10px;">Clear</button>
            </div>

        </div>

        <div>
            <label for="private-key-input" class="label">4) Sign Logic Signature</label>
            <p>To securely authorize the transaction, please input the private key correspondent to your account to sign the logic signature. 
            <br>This step is essential for delegating the necessary permissions and to authorize the receiver to spend funds on your account.
            <br>
            <br>Upon successful signing, you will see your logic signature encoded in the text area "Your SMS Text", after: "Your Token." </p>
            <input type="password" id="private-key-input" name="private-key-input" placeholder="Enter your private key">
    
            <br><button onclick="signLogicSignature()">Sign</button>
            <div id="signature-notification"></div>
        </div>

        <br>
        <h2>Send Token via SMS</h2>
        <div>
            <label for="encoded-lsig" class="label">5) Text Preparation</label><br>
            <h3 id="encoded-lsig"> Your SMS Text: </h3>
            <p>Here will appear the text that will be sent via SMS.\n
            Please verify the correctness of account address and  amount before sending.
            </p>
            <textarea id="encoded-lsig-output" placeholder="Here will appear the text to be sent via SMS" readonly></textarea>
        </div>

        <div>
            <label for="phone-section" class="label">6) Enter Receiver's Phone Number</label><br>
            <p>Finally, to send the SMS, enter the phone number of the receiver. The phone number must not have special characters or spaces, like: 447566223444
            <br>
            <br><strong>Please double-check the receiver's phone number before sending. This action cannot be undone.</strong></p>
            <div id="phone-section">
                <input type="tel" id="phone-number-input" name="phone-number-input" placeholder="Enter phone number" pattern="[0-9]{10}">
                <button onclick="sendSMS()">Send SMS</button>
                <button id="clear-phone-input" style="margin-right: 10px;">Clear</button>
                <span id="sms-notification"></span>
        </div>
        `);
        bindDynamicEvents();
    });

    $('#validate-transaction').click(function() {
        $('#dynamic-content').empty();
        $('#dynamic-content').html(`
        <p>To receive a token via SMS, the user will need to send a message to this number: <strong>+447451281414</strong>.
        <br>Once the message is sent to this number, it will be received by the program and undergo a series of steps to be parsed and authenticated.</p>
        <p>Here's the process broken down into steps:</p>
        <ol>
            <li><strong>Parse the SMS:</strong> The message received will be parsed to extract the necessary data. This involves interpreting the content of the message to separate out the encoded logic signature (lsig)<br>and any other relevant information contained in the SMS.</li>
            <li><strong>Decode the encoded lsig:</strong> This decoding step converts the transmitted data back into a format that the program can use for further processing and verification. Then, get a LogicSig object<br>and save it into the session's data. </li>
            <li><strong>Create a Transaction:</strong> Specify the sender and receiver addresses and the amount. Finally, the transaction will use the lsig object retrieved from the session data.<br>This object is crucial for signing the transaction and authenticating it as valid and authorized.</li>
        </ol>

        <h2>Receive SMS Text with Token</h2>
        <div>
            <label for="sms-data-output" class="label">1) Fetch Message Data</label><br>
            <p>Please click on 'Fetch SMS Data' below to display the SMS text received.</p>
            <textarea id="sms-data-output" placeholder="This area is to display text and metadata of the incoming SMS." readonly></textarea>
                <div>
                    <button onclick="fetchAndDisplaySMSData()">Fetch SMS Data</button>
                    <button id="clear-sms-data" style="margin-right: 10px;">Clear</button>
                </div>
        </div>

        <div>
            <label for="decode-lsig-output" class="label">2) Decode Logic Signature</label><br>
            <div>
                <p>Press the below button to start the decoding process. This will decode the encoded token in a Logic Signature Object.</p>
                <button onclick="fetchAndDisplayDecodedLsig()">Decode Logic Sig</button>
                </div>
                <span id="decoding-notification"></span>
        </div>
        

        <h2>Create Transaction</h2>

        <p>Finally, create a transaction specifying its parameters - Sender's Account, Receiver's Account, Amount.</p>
        <div>
            <form id="fetch-form-sender" action="javascript:void(0);">
                <label for="sender-address-input" class="label-txn">1) Sender's Account Address:</label><br>
                <input type="text" id="sender-address-input" name="sender-address-input" placeholder="Enter Sender's Account Address Here">
                <input type="submit" id="fetch-account-info" value="Fetch Account Info">
            </form>
        
            <textarea id="sender-output" readonly></textarea>
            <button id="clear-s-address-input" style="margin-right: 10px;">Clear</button>

        </div>

        <div>
            <form id="fetch-form-receiver" action="javascript:void(0);">
                <label for="receiver-address-input" class="label-txn">2) Receiver's Account Address:</label><br>
                <input type="text" id="receiver-address-input" name="receiver-address-input" placeholder="Enter Receiver's Account Address Here">
                <input type="submit" value="Fetch Account Info">
            </form>

            <textarea id="receiver-output" readonly></textarea>
            <button id="clear-r-address-input" style="margin-right: 10px;">Clear</button>
        </div>

        <div>
            <label for="amount-input" class="label-txn">3) Amount:</label><br>
            <p>Specify an amount in microAlgos (1 microAlgo = 0.001 Algos)</p>
            <input type="number" id="amount-input" name="amount-input" placeholder="Enter Amount in microAlgos" step="0.01" min="0"><br>
            <button onclick="createTransaction()">Create Transaction</button>
            <span id="txn-notification"></span>
        </div>
        `)
        bindDynamicEvents();
    });
});


// Fetch and update elements in the webpage without reloading it
function bindDynamicEvents() {

    // Fetch sender's account info (in 'Send Token' page)
    $('#fetch-form-s-sender').submit(function(event) {
        // prevent page from reloading
        event.preventDefault();

        $.ajax({
            url: '/fetch_account',
            type: 'POST',
            data: {account_to_fetch: $('#s-address-input').val()},
            success: function(response) {
                $('#s-output').val(`${response.fetched_account_info}`);
            },
            error: function(response) {
                $('#s-output').val(response.responseJSON.error);
            }
        });
    });

    // Fetch sender's account info (in 'Receive Token' page)
    $('#fetch-form-sender').submit(function(event) {
        event.preventDefault();

        $.ajax({
            url: '/fetch_account',
            type: 'POST',
            data: {account_to_fetch: $('#sender-address-input').val()},
            success: function(response) {
                $('#sender-output').val(`${response.fetched_account_info}`);
            },
            error: function(response) {
                $('#sender-output').val(response.responseJSON.error);
            }
        });
    });

    // Fetch receiver's account info (in 'Receive Token' page)
    $('#fetch-form-receiver').submit(function(event) {
        event.preventDefault();
        $.ajax({
            url: '/fetch_account',
            type: 'POST',
            data: {account_to_fetch: $('#receiver-address-input').val()},
            success: function(response) {
                $('#receiver-output').val(`${response.fetched_account_info}`);
            },
            error: function(response) {
                $('#receiver-output').val(response.responseJSON.error);
            }
        });
    });

    // Generate a new account for the sender
    $('#generate-account').click(function(event) {
        event.preventDefault();
        $.ajax({
            url: '/generate_account',
            type: 'GET',
            success: function(response) {
                $('#s-address-input').val(response.new_account_address);
                $('#s-output').val('Find address, private key, and mnemonics of newly generated address in file "generated_accounts.txt"\n\nRemember that after generation, an account needs to hold funds to officially exist.\nConsider funding your account with escrow funds at: https://bank.testnet.algorand.network');
            },
            error: function(response) {
                $('#s-output').val('Error generating new account');
            }
        });
    });

    // Submit teal contract
    $('#teal-form').on('submit', function(event) {
        event.preventDefault();
    
        var formData = new FormData(this);
        fetch('/upload', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('notification-teal').innerHTML = `<p class="error">Error: ${data.error}</p>`;
            } else {
                document.getElementById('notification-teal').innerHTML = `The contract you have uploaded has an amount of ${data.amount} microAlgos`;
                document.getElementById('amount-hidden').value = data.amount;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('notification-teal').innerHTML = `<p class="error">Error: ${error.message}</p>`;
        });
    });

    // Clear fields
    
    $('#clear-ss-address-input').click(function() {
        $('#s-address-input').val('');
        $('#s-output').val('');
    });

    $('#clear-s-address-input').click(function() {
        $('#sender-address-input').val('');
        $('#sender-output').val('');
    });

    $('#clear-r-address-input').click(function() {
        $('#receiver-address-input').val('');
        $('#receiver-output').val('');
    });

    $('#clear-phone-input').click(function() {
        $('#phone-number-input').val('');
    });

    $('#clear-sms-data').click(function() {
        $('#sms-data-output').val('');
    });
}

// Generate the LogicSignature from TEAL file
function generateLogicSignature() {
    var formData = new FormData(document.getElementById('teal-form'));
    fetch('/generate_logic_signature', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('notification').innerHTML = `<p>${data.message}</p>`;
        } else {
            document.getElementById('notification').innerHTML = `<p class="error">${data.message}</p>`;
            document.getElementById('output-lsig').innerHTML = `<p class="error">${data.message}</p>`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('notification').innerHTML = '<p class="error">Failed to generate Logic Signature.</p>';
    });
}

// Check whether smart contract is uploaded and if the address provided matches the private key.
// If so, sign the logic signature.
function signLogicSignature() {
    var privateKey = document.getElementById('private-key-input').value;
    var accountAddress = document.getElementById('s-address-input').value;
    var fileInput = document.getElementById('file-upload');
    var amount = document.getElementById('amount-hidden').value;
    
    if (fileInput.files.length === 0) {
        document.getElementById('signature-notification').innerHTML = '<p class="error">Please upload a TEAL contract before signing.</p>';
        return;
    }

    if (!accountAddress) {
        document.getElementById('signature-notification').innerHTML = '<p class="error">Please provide an account address.</p>';
        return;
    }

    if (!privateKey) {
        document.getElementById('signature-notification').innerHTML = '<p class="error">Please provide a private key.</p>';
        return;
    }

    // route to verify the matching between account's address and private key
    fetch('/verify_private_key', {
        method: 'POST',
        // specify to the server will receive a JSON obj
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ privateKey: privateKey, accountAddress: accountAddress }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.isValid) {
            // route to sign the lsig
            fetch('/sign_lsig', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ privateKey: privateKey }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    var outputText = `Amount: ${amount} microAlgos\nFrom Address: ${accountAddress}\nYour Token: ${data.final_lsig}`;
                    document.getElementById('encoded-lsig-output').value = outputText;
                    $('#signature-notification').text("Successfully Signed Logic Signature. See it in the output area below");
                } else {
                    $('#signature-notification').text("Failed to Sign Logic Signature.");
                }
            })
        } else {
            document.getElementById('signature-notification').innerHTML = '<p class="error">Private key not matching account address.</p>';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('signature-notification').innerHTML = '<p class="error">Private key not matching account address.</p>';
    });
}


// Send SMS with signed lsig
function sendSMS() {
    var phoneNumber = $('#phone-number-input').val();
    var text = $('#encoded-lsig-output').val();

    // validate phone number
    if (phoneNumber.length !== 12 || isNaN(phoneNumber)) {
        alert("Please enter a valid phone number with a 2-digit national prefix followed by a 10-digit phone number.");
        return;
    }

    // route to send sms
    fetch('/send_sms', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            receiver_number: phoneNumber,
            text: text
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            $('#sms-notification').text("Message successfully sent.");
        } else {
            $('#sms-notification').text("Failed to send the message.");
        }
    })
    .catch(error => {
        console.error('Error sending SMS:', error);
        $('#sms-notification').text("Error sending the message.");
    });
}

// Fetch and display the SMS message received
function fetchAndDisplaySMSData() {
    fetch('/fetch_sms_data')
    .then(response => response.json())
    .then(data => {
        document.getElementById('sms-data-output').value = 
        `${data.message_text}

From: ${data.sender_number}

To: ${data.receiver_number}

Timestamp: ${data.timestamp}`;
    })
    .catch(error => {
        console.error('Error fetching SMS data:', error);
    });
}

// Decode SMS string from text message to LogicSig object
function fetchAndDisplayDecodedLsig() {
    fetch('/decode_lsig')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            var displayText = `Amount: ${data.amount} microAlgos\n\nFrom Address: ${data.address}\n\nDecoding status: ${data.message}`;
            document.getElementById('sms-data-output').textContent = displayText;
            document.getElementById('sender-address-input').value = data.address;
            $('#decoding-notification')
            .html("Successfully decoded the Logic Signature.<br><br>Please note that the Delegator's address has been set in the field below.<br><br> Your Token is now ready to be used, for a maximum spending amount of " 
            + data.amount + " microAlgos")
        } else {
            $('#decoding-notification').text(`Failed to decode: Check the presence and correctness of the token`);
            document.getElementById('sms-data-output').textContent = `Decoding status: ${data.message}`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        $('#decoding-notification').text('Error fetching decoded LSIG.');
        document.getElementById('sms-data-output').textContent = 'Error fetching decoded LSIG.';
    });
}


// Create a transaction
function createTransaction(senderAddress, receiverAddress, amount) {
    var senderAddress = $('#sender-address-input').val();
    var receiverAddress = $('#receiver-address-input').val();
    var amount = parseInt($('#amount-input').val(), 10);
    
    // check if all the parameters are present
    if (!senderAddress || !receiverAddress || isNaN(amount)) {
        $('#txn-notification').text("Sender address, receiver address, and amount are required.");
        return;
    }

    // notification for waiting confirmation after submission
    $('#txn-notification').text("The transaction is waiting for confirmation.");

    fetch('/create_transaction', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        // working with a JSON string, http works with data in string format
        body: JSON.stringify({
            sender_address: senderAddress,
            receiver_address: receiverAddress,
            amount: amount
        }),
    })
    // expects a JSON response
    .then(response => response.json())
    // operate with the data parsed
    .then(data => {
        if (!data.success) {
            throw new Error(data.message);
        }
        $('#txn-notification').text(data.message);
        $('#sms-data-output').val('');
        $('#sender-address-input').val('');
        $('#sender-output').val('');

    })
    .catch(error => {
        console.error('Error creating transaction:', error);
        $('#txn-notification').text(error.message);
    });
}