import requests
import pandas as pd
import json
import matplotlib.pyplot as plt
plt.style.use('ggplot')

class SNOTEL:

	def __init__(self):

		self.api = 'http://api.powderlin.es/'
		self.stations = requests.get(self.api + 'stations')

	def process_stations(self):

		self.df_stations = pd.DataFrame.from_records(self.stations.json())
		self.num_stations = self.df_stations.shape[0]

		# Removing location for clean up
		location = self.df_stations['location']
		self.df_stations = self.df_stations.drop(columns=['location'])

		# Cleaning up location
		lat = []
		lng = []
		for i in location:
			lat.append(i['lat'])
			lng.append(i['lng'])

		# Concatonating to df_stations
		self.df_stations['lat'] = lat
		self.df_stations['lng'] = lng

	def download_sites(self, num_days):

		# Total data
		self.site_data = {}
		for i in range(self.num_stations):
			if i % 100 == 0:
				print(f'Downloaded {i} stations...')

			try:
				# Grab individual site
				site = requests.get(self.api + 'station/' + self.stations.json()[i]['triplet'], params={'days':num_days}).json()

				# Extracting the data and storing it into a dataframe
				data = site['data']
				df_site = pd.DataFrame.from_records(data)
				# Storing individual site into a dictionary
				self.site_data[self.df_stations['name'][i]] = df_site

			except ValueError:

				# Don't store station if it throws a ValueError (JSONDecodeError in this case)
				print(f'Station: {self.df_stations["name"][i]} (Index: {i}) is no longer supported (Internal Server Error).')

	def graph_site(self, site_key, save_path=None):

		df_site = self.site_data[site_key]

		snow_water_equivalent = df_site['Snow Water Equivalent (in)']
		change_snow_water_equivalent = df_site['Change In Snow Water Equivalent (in)']
		snow_depth = df_site['Snow Depth (in)']
		change_snow_depth = df_site['Change In Snow Depth (in)']
		air_temp = df_site['Observed Air Temperature (degrees farenheit)']

		# Setting up figure
		fig, axs = plt.subplots(2, 3,figsize=(16,9))
		fig.delaxes(axs[1,2])
		fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.2, hspace=0.3)
		fig.suptitle(site_key, fontsize=20)

		# SWE
		axs[0,0].plot(snow_water_equivalent, c='tab:blue')
		axs[0,0].set_xlabel('Time')
		axs[0,0].set_ylabel('Values')
		axs[0,0].set_title('Snow Water Equivalent (in)')

		# Change in SWE
		axs[0,1].plot(change_snow_water_equivalent, c='tab:red')
		axs[0,1].set_xlabel('Time')
		axs[0,1].set_ylabel('Values')
		axs[0,1].set_title('Change in Snow Water Equivalent (in)')

		# Snow Depth
		axs[0,2].plot(snow_depth, c='tab:green')
		axs[0,2].set_xlabel('Time')
		axs[0,2].set_ylabel('Values')
		axs[0,2].set_title('Snow Depth (in)')

		# Change in Snow Depth
		axs[1,0].plot(change_snow_depth, c='tab:orange')
		axs[1,0].set_xlabel('Time')
		axs[1,0].set_ylabel('Values')
		axs[1,0].set_title('Change in Snow Depth (in)')

		# Air Temperature
		axs[1,1].plot(air_temp, c='tab:brown')
		axs[1,1].set_xlabel('Time')
		axs[1,1].set_ylabel('Values')
		axs[1,1].set_title('Air Temperature (F)')