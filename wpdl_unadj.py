import sys
import subprocess
import os
import argparse
from wplib.utils.convenience_functions import download_country_covariates as dl
from total_population_dict import total_pop_dict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class MultByUNadj:
	"""Class to download WorldPop population per pixel (ppp) raster and multiply by UN Adjusted rates"""

	def __init__(self, iso, year, n, download_loc, keep_original_raster=True):
		"""
		Instanatiation of the class

		iso --> Alphanumeric iso for country (3 characters)
		year --> define Year to download (2000 - 2020)
		n --> Number user will multiply by raster to get UN adj rates
		download_loc --> Location in which to save download and UNAdj output
		keep_original_raster --> Default = True; if False downloaded ppp will be deleted.
		"""
		self.iso = iso
		self.year = int(year)
		self.year_cut = int(str(year)[-2:])
		self.n = float(n)
		if self.iso in total_pop_dict.keys():
			self.total_pop = total_pop_dict[self.iso][self.year_cut]
		else:
			self.total_pop = None
		self.download_loc = download_loc
		self.keep_original_raster = keep_original_raster
		self.ppp_raster_name = '{0}_grid_100m_ccilc_dst011_{1}.tif'.format(self.iso.lower(), self.year) ####This needs to be replaced with PPP name when ready
		#self.ppp_raster_name = '{0}_wpgp_ppp_{1}.tif'.format(self.iso.lower(), self.year) ####This needs to be replaced with PPP name when ready

	def download_raster(self, iso, year):
		"""
		Download ppp raster from WP FTP
		
		Arguments:
		iso --> Alphanumeric iso for country (3 characters)
		year --> define Year to download (2000 - 2020)

		Returns
		None
		"""
		if self.total_pop:
			dl_raster_name = 'ccilc_dst011_{0}'.format(year) ###Need to replace this with popualation raster grc_grid_100m_ghsl_guf_2012.tif
			#dl_raster_name = #################ADD CORRECT RASTER NAME #########################
			dl(iso, self.download_loc, [dl_raster_name])
			print('Downloaded')
			
		else:
			print("{0} is currently unavailable for download.".format(iso))

	def multiply_by_unAdj(self, ppp_raster_name):
		"""
		Multiply ppp raster by UN Adj value (user supplied --> self.n)
		UNAdj = (ppp * n)/total population
		"""
		#input_raster = os.path.join(self.download_loc, self.ppp_raster_name)
		input_raster = ppp_raster_name
		output_raster = os.path.join(self.download_loc, "{0}_UNAdj_ppp_{1}.tif".format(self.iso.lower(), self.year))
		equation = '(A * {0})/{1}'.format(self.n, self.total_pop)
		gdal_command = 'gdal_calc.py -A {0} --outfile={1} --calc="{2}" --NoDataValue=9999 --co COMPRESS=LZW --co PREDICTOR=2 --co BIGTIFF=YES'.format(input_raster, output_raster, equation)
		subprocess.call(gdal_command, shell=True)
		if self.keep_original_raster == False:
				os.remove(os.path.join(self.download_loc, input_raster)) #################ADD CORRECT RASTER NAME #########################


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Download ppp rasters to WorldPop FTP and multiply by user-defined UNAdj rate.")
	parser.add_argument("ISO", help="ISO of country (3 characters).")
	parser.add_argument("Year", help="Year to download (2000-2020).")
	parser.add_argument("n", help="UN value with which to adjust the population.")
	parser.add_argument("download_loc", help="Location where ppp will be downloaded and adjusted raster will be saved.")
	parser.add_argument("--keep_raster", help="Boolean (default=True) to define whether to delete the unadjusted raster after calculating the downloaded raster.", choices=['True', 'False'])
	args = parser.parse_args()

	print(args.ISO)
	print(args.download_loc)

	if not args.keep_raster:
		args.keep_raster = True
	elif args.keep_raster == "True":
		args.keep_raster = True
	else:
		args.keep_raster = False

	test_dl = MultByUNadj(args.ISO, args.Year, args.n, args.download_loc, args.keep_raster)
	test_dl.download_raster(test_dl.iso, test_dl.year)
	test_dl.multiply_by_unAdj(os.path.join(test_dl.download_loc, test_dl.ppp_raster_name))

