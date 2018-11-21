# item_catalog

The Item Catalog project is a Web application that provides a data base to allow user to form a catalog with categories having brands and the related description of the brands, wherein the user can login with google account and can only edit the content they created.



## Related code and function
- Python
- HTML
- CSS
- Flask
- SQLAchemy
- OAuth
- Google Login


# Getting Started

##PreRequisites
- Python 2.7 (https://www.python.org/download/releases/2.7/)
- Vagrant (https://www.vagrantup.com/)
- VirtualBox (https://www.virtualbox.org/wiki/Downloads)
- Udacity Vagrantfile (https://github.com/udacity/fullstack-nanodegree-vm)

##Setup
- Install Vagrant and VirtualBox
- Download or Clone the Vagrantfile from the Udacity Repo
- Clone this repo as item_catalog, and put it into the vagrant directory which is shared with your virtual machininto the Vagrant directory
- cd to item_catalog directory and use the following command to launch the Vagrant VM:
	`$ vagrant up`
	`$ vagrant ssh`
- cd into the vagrant directory and use the command following command to build the category database on your system:
	`python database_setup.py`
- use the following command to run the website app:
  `python application.py` from within its directory
- use your browser to go to `http://localhost/5000` to access the application
- for the first time use, please click login on the right hand side to login and add a category, such as "Manufacture Watch Brand", and then you can add different brands related to the category, such as "Rolex".

## JSON Endpoints

- use the following command to return information of all categories in JSON:
`http://localhost/5000/categories/JSON`

- use the following command to return information of all brands of a category in JSON:
`http://localhost/5000/category/<int:category_id>/JSON`

- use the following command to return information of a brand in JSON:
`http://localhost/5000/category/<int:category_id>/<int:brand_id>/JSON`

##Reference
- https://github.com/udacity/ud330
