# Deploy Database
# echo "Begin to setup Mysql"
# echo "grant all privileges on *.* to 'wp-cms'@'localhost' identified by '753951';" | mysql -uroot -psniper
# echo "drop database cmsdb; create database cmsdb;" | mysql -uroot -psniper

# Install plugins
echo "Begin install wordpress plugins"
PLUGIN_DIR="content/plugins"
 
plugins="all-in-one-seo-pack google-sitemap-generator feedwordpress simple-page-ordering secure-wordpress hierarchy image-widget wp-super-cache register-plus-redux regenerate-thumbnails taxonomy-taxi custom-post-type-ui wordpress-importer password-protect-wordpress wp-quick-pages simple-page-ordering woocommerce alipay-for-woocommerce" 

for plugin in ${plugins}
do
    echo "Fetching ${plugin}...";
    wget --quiet http://downloads.wordpress.org/plugin/${plugin}.zip;
    unzip -q ${plugin}.zip;
    mv ${plugin} ${PLUGIN_DIR}
done

# Cleanup
echo "Cleaning up temporary files and directories...";
rm *.zip

echo "Done!";   

