import subprocess
import yaml
import tempfile

# import_path, app_name, route_prefix
APPS_TO_BUILD = [
    ('translator_app', 'translator', '/translator'),
    ('greeting_app', 'greeting', '/greeting'),
]

def generate_multi_app_config(output_file="config.yaml"):

    combined_apps = []

    for import_path, name, route in APPS_TO_BUILD:
        print(f"🛠  Building config for {name}...")

        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp:
            tmp_path = tmp.name
        
        # 2. Execute 'serve build' and capture the output string
        subprocess.run(
            ["serve", "build", f"main:{import_path}", "-o", tmp_path],
            check=True,
            stderr=subprocess.DEVNULL
        )

        with open(tmp_path, "r") as f:
            app_config = yaml.safe_load(f)
        
        # 3. Extract the application block and override values
        # serve build always returns a dict with an 'applications' list containing 1 item
        if "applications" in app_config and len(app_config["applications"]) > 0:
            app_data = app_config["applications"][0]
            
            # Replace/Add your custom values
            app_data["name"] = name
            app_data["route_prefix"] = route
            
            combined_apps.append(app_data)

    # Create the final multi-app structure
    final_config = app_config
    final_config['applications'] = combined_apps

    # Write to file
    with open(output_file, "w") as f:
        yaml.dump(final_config, f, sort_keys=False)
    
    print(f"✅ Success! {output_file} created with {len(combined_apps)} applications.")

if __name__ == "__main__":
    generate_multi_app_config()