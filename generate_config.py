import subprocess
import yaml
import tempfile


class LiteralStr(str):
    pass

def literal_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")

yaml.add_representer(LiteralStr, literal_representer)

# import_path, app_name, route_prefix
APPS_TO_BUILD = [
    ('translator_app', 'translator', '/translator'),
    # ('greeting_app', 'greeting', '/greeting'),
    ('chain_app', 'chain', '/chain'),
    ('stream_app', 'stream', '/stream'),
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

    # Write to file (for local serve test)
    with open(output_file, "w") as f:
        yaml.dump(final_config, f, sort_keys=False)

    print(f"✅ Success! {output_file} created with {len(combined_apps)} applications.")

    # Update k8s/ray_service.yaml spec.serveConfigV2
    ray_service_path = "k8s/ray_service.yaml"
    with open(ray_service_path, "r") as f:
        ray_service = yaml.safe_load(f)

    serve_config = yaml.safe_load(ray_service["spec"]["serveConfigV2"])
    serve_config["applications"] = combined_apps
    ray_service["spec"]["serveConfigV2"] = LiteralStr(yaml.dump(serve_config, sort_keys=False))

    with open(ray_service_path, "w") as f:
        yaml.dump(ray_service, f, sort_keys=False)

    print(f"✅ Success! {ray_service_path} serveConfigV2 updated with {len(combined_apps)} applications.")

if __name__ == "__main__":
    generate_multi_app_config()