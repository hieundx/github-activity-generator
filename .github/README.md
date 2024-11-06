A script that helps you *instantly* generate a beautiful GitHub Contributions Graph
for the last year.

## ⚠ Disclaimer
This script doesn't encourage you to cheat. Cheating is bad. But if anybody judges your professional skills by
the graph on your GitHub profile (which carries no value), they deserve to see a rich graph.

## What it looks like

### Before :neutral_face: :no_mouth: :unamused: 
![Before](before.png)
### After :muscle: :relieved: :heart: :sunglasses: :metal: :horse: :wink: :fire: :dancer: :santa: :fireworks: :cherries: :tada:
![After](after.png)

# Prerequisites
- Github CLI: https://cli.github.com/
- SSH authentication with Github: 
    - https://docs.github.com/en/authentication/connecting-to-github-with-ssh
    - `gh auth login`

## How to use
1. Create an empty GitHub repository. Do not initialize it.
2. Clone this repository
3. Create a virtual environment or conda environment
4. Install dependencies `pip install -r requirements.txt`
5. Run `python gui.py`

## How it works
The script initializes an empty git repository, creates a text file and starts 
generating changes to the file for every day within the last year (0-20 commits 
per day). Once the commits are generated it links the created repository with
the remote repository and pushes the changes.

## Making contributions private

You might want to make the generated repository private. It is free
on GitHub. You only need to set up your account 
[to show private contributions](https://help.github.com/en/articles/publicizing-or-hiding-your-private-contributions-on-your-profile).
This way GitHub users will see that you contributed something, but they won't be
able to see what exactly.

## Troubleshooting
#### I performed the script but my GitHub activity is still the same.
It might take several minutes for GitHub to reindex your activity. Check
if the repository has new commits and wait a couple of minutes.
#### The changes are still not reflected after some time.
Are you using a private repository? If so, enable showing private contributions
[following this guide](https://help.github.com/en/articles/publicizing-or-hiding-your-private-contributions-on-your-profile).

#### Still no luck
Make sure the email address you have in GitHub is the same as you have in
your local settings. GitHub counts contributions only when they are made 
using the corresponding email.

Check your local email settings with:
```
git config --get user.email
```
If it doesn't match with the one from GitHub reset it with
```
git config --global user.email "user@example.com"
```
Create a new repository and rerun the script.

#### There are errors in the logs of the script.
Maybe you tried to use an existing repository. If so, make sure you are using
a new one which is *not initialized*.

**If none of the options helped, open an issue and I will fix it as soon as possible.**
