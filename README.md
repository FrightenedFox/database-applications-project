# database-applications-project
Database aplications project based on usos.edu.pl

# Server instructions

## Create SSH key: 

Generate a new SSH key by following [**Generating a new SSH key**](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key) instructions. 

Then add that key to your GitHub account, by following [**Adding a new SSH key to your account**](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account#adding-a-new-ssh-key-to-your-account) instructions. 

If you've done everything correctly, than you should see your SSH public key on your GitHub `https://github.com/<Your-GitHub-Account>.keys` page. Example: https://github.com/FrightenedFox.keys.

## Login with SSH and switch to key authentication

```bash
ssh <user>@<ip-address>
# Enter password given to you

# Setup authentication with SSH key
curl https://github.com/<Your-GitHub-Account>.keys >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 644 ~/.ssh/authorized_keys

# You can also change your Linux user password using this command
passwd
# Enter password given to you and then imagine new Linux user password. 
# You will use this password when running "sudo" commands. 

exit
```

Check if everything works:

```bash
ssh <user>@<ip-address>
# Enter passphrase (password) you assigned to your SSH key.
```

## Login into `psql`

```bash
psql -U <user> -d <database>
# For example 
psql -U ncyran -d postgres
```
