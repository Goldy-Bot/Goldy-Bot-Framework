:og:description: In goldy bot instead of cogs or whatever you may call them we have extensions.
   Extensions are.... well.... EXTENSIONS! They are modules that extend the goldy bot framework.

➕Extensions
==============

⭐ How to create an Extension:
-------------------------------
In goldy bot instead of cogs or whatever you may call them we have extensions.

   Extensions are.... well.... EXTENSIONS! They are modules that extend the goldy bot framework. 
   You can create an extension for ANYTHING, a music bot, commands to lookup game stats and a lot more exciting commands. ☁ The skies your limit.

Here are quick examples to get started with extensions in Goldy Bot V5. 🌟

.. tab:: Python (Native)

   This is GoldyBot v5 extension done natively within python. 😊

   .. code-block:: python

      import GoldyBot

      class YourExtension(GoldyBot.Extension):
         def __init__(self):
            super().__init__()

         @GoldyBot.command()
         async def hello(self, platter: GoldyBot.GoldPlatter):
            await platter.send_message("👋hello", reply=True)

      def load():
         YourExtension()

.. tab:: Javascript API (Coming Soon...)

   This is a GoldyBot v5 extension done within javascript using our ``GBExtension.js`` API that's going to be coming soon. 😊

   .. code-block:: javascript

      class YourExtension extends GoldyBot.Extension {
         constructor() {
            super();
         }

         async hello(platter) {
            await platter.send_message("👋hello", {
               "reply": true
            });
         }
      }

      function load() {
         new YourExtension();
      }

Neat right 😁.

.. note::

   The javacript api is not written yet so the code in this example is subject to massively change. This is only a mockup.


Extensions
------------
.. automodule:: GoldyBot.goldy.extensions
   :members:
   :undoc-members:
   :show-inheritance:

Extension Loader
-----------------
.. automodule:: GoldyBot.goldy.extensions.extension_loader
   :members:
   :undoc-members:
   :show-inheritance: