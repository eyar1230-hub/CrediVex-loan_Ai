import os
import re

js_path = r'C:\Users\eyar1\ECOM\antigravity works\Project_Loan\static\js\main.js'
with open(js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace block 1: Resetting UI
old_reset = '''    // Reset UI
    loading.style.display = 'block';
    errorPanel.style.display = 'none';'''

new_reset = '''    // Reset UI
    errorPanel.style.display = 'none';
    resultsPanel.style.display = 'none';
    errorList.innerHTML = '';
    resultsTable.innerHTML = '';

    loading.style.display = 'block';
    const progressBar = document.getElementById('bulkProgressBar');
    const progressText = document.getElementById('bulkProgressText');
    const progressDetail = document.getElementById('bulkProgressDetail');
    
    progressBar.style.width = '0%';
    progressText.innerText = '0%';
    progressDetail.innerText = 'Uploading file to server...';

    let progress = 0;
    const progressInterval = setInterval(() => {
        if (progress < 30) {
            progress += Math.floor(Math.random() * 8) + 4;
            progressDetail.innerText = 'Parsing data and validating rows...';
        } else if (progress < 60) {
            progress += Math.floor(Math.random() * 5) + 2;
            progressDetail.innerText = 'Running SVC Model Inference...';
        } else if (progress < 85) {
            progress += Math.floor(Math.random() * 3) + 1;
            progressDetail.innerText = 'Calculating probability scores...';
        } else if (progress < 95) {
            progress += 1;
            progressDetail.innerText = 'Finalizing risk tiers...';
        }
        
        if (progress > 95) progress = 95;
        
        progressBar.style.width = progress + '%';
        progressText.innerText = progress + '%';
    }, 500);'''

content = content.replace('''    // Reset UI
    loading.style.display = 'block';
    errorPanel.style.display = 'none';
    resultsPanel.style.display = 'none';
    errorList.innerHTML = '';
    resultsTable.innerHTML = '';''', new_reset)


# Replace block 2: Hiding loading and showing results
old_success = '''        const data = await response.json();
        
        loading.style.display = 'none';'''

new_success = '''        const data = await response.json();
        
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        progressText.innerText = '100%';
        progressDetail.innerText = 'Processing Complete!';
        
        await new Promise(r => setTimeout(r, 600)); // Let the 100% animation finish
        loading.style.display = 'none';'''

content = content.replace(old_success, new_success)


# Replace block 3: Catch block
old_catch = '''    } catch (err) {
        loading.style.display = 'none';'''

new_catch = '''    } catch (err) {
        clearInterval(progressInterval);
        loading.style.display = 'none';'''

content = content.replace(old_catch, new_catch)


with open(js_path, 'w', encoding='utf-8') as f:
    f.write(content)
