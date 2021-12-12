echo cd is %cd%
set save_dir=%cd%
echo save_dir is %save_dir%
cd Tensorflow\labelimg
echo cd is %cd%
python labelImg.py

echo cd is %cd%
cd %save_dir%
echo cd is %cd%
