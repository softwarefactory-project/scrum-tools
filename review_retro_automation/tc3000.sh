#!/usr/bin/env sh

_SPRINT=$(date +%Y-%V)

# TODO
# - dry-run mode
# - state save in case of failure for replayability

interactive_args() {
    read -p "Please enter the sprint's name (default $_SPRINT): " SPRINT
    if [ -z "$SPRINT" ]; then
        SPRINT=$_SPRINT
    fi
}
    read -p "Please enter the path to your text editor (default $EDITOR): " TXTEDITOR
    if [ -z "$TXTEDITOR" ]; then
        TXTEDITOR=$EDITOR
    fi

interactive_args

echo "Fetching pads ..."
./pads2summaries.py 2018-22 prepare

read -n 1 -s -r -p "You will now have a chance to edit files manually. Press any key to continue ..."
$TXTEDITOR /tmp/${SPRINT}_daily_blog_internal.html /tmp/${SPRINT}_retro_blog_internal.html /tmp/${SPRINT}_review_blog_internal.html /tmp/${SPRINT}_review_blog_public.rst /tmp/${SPRINT}_review_email_public.txt /tmp/${SPRINT}_review_email_internal.txt
echo ""
read -n 1 -s -r -p "Press any key to publish to Mojo and send emails ..."
echo ""
echo ""
read -p "Please enter your kerberos login (default $USER): " USERNAME
if [ -z "$USERNAME" ]; then
    USERNAME=$USER
fi
curl -u $USERNAME https://mojo.redhat.com/servlet/JiveServlet/downloadBody/1172175-102-1-2239214/google_TC_automation.json -o /tmp/gmail_secret.json
./pads2summaries.py 2018-22 publish $USERNAME
rm /tmp/gmail_secret.json
echo ""
echo "Publishing to SF website ..."
git clone --depth 1 https://softwarefactory-project.io/r/www.softwarefactory-project.io.git /tmp/publish_automation
d=$(pwd)
cd /tmp/publish_automation
cp /tmp/${SPRINT}_review_blog_public.rst website/content/${SPRINT}.rst
git add website/content/${SPRINT}.rst
git commit -m"${SPRINT} summary"
git review
cd $d
rm -rf /tmp/publish_automation
rm /tmp/${SPRINT}_daily_blog_internal.html /tmp/${SPRINT}_retro_blog_internal.html /tmp/${SPRINT}_review_blog_internal.html /tmp/${SPRINT}_review_blog_public.rst /tmp/${SPRINT}_review_email_public.txt /tmp/${SPRINT}_review_email_internal.txt
echo ""
echo ""
echo "Things to do manually:"
echo ""
echo "* Save and clean up the pads"
