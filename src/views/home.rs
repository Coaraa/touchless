use eframe::egui;
use crate::app::View;
use reqwest;


pub fn show(ctx: &egui::Context, current_view: &mut View) {
    let dark_blue = egui::Color32::from_rgb(31, 40, 51);

    let main_frame = egui::Frame::none().fill(dark_blue).inner_margin(20.0);

    egui::CentralPanel::default().frame(main_frame).show(ctx, |ui| {

        ui.horizontal(|ui| {

            // --- PARTIE GAUCHE : La carte blanche ---
            let left_width = ui.available_width() * 0.6;

            let left_frame = egui::Frame::none()
                .fill(egui::Color32::WHITE)
                .rounding(20.0)
                .inner_margin(40.0);

            left_frame.show(ui, |ui| {
                ui.set_width(left_width);

                ui.vertical(|ui| {
                    let gear_btn = egui::Button::new(egui::RichText::new("⚙ Paramètres").size(16.0).color(egui::Color32::BLACK)).frame(false);
                    if ui.add(gear_btn).clicked() {
                        *current_view = View::Settings;
                    }

                    ui.add_space(80.0);

                    ui.heading(egui::RichText::new("Touchless").size(50.0).strong().color(egui::Color32::BLACK));
                    ui.add_space(10.0);
                    ui.label(egui::RichText::new("Contrôle gestuel sans contact des commandes de votre PC.").size(18.0).color(egui::Color32::DARK_GRAY));

                    ui.add_space(50.0);

                    let block_frame = egui::Frame::none()
                        .fill(egui::Color32::from_rgb(245, 247, 246))
                        .rounding(10.0)
                        .inner_margin(20.0);

                    block_frame.show(ui, |ui| {
                        ui.set_width(ui.available_width());

                        ui.horizontal(|ui| {
                            let icon_frame = egui::Frame::none().fill(egui::Color32::BLACK).rounding(10.0).inner_margin(15.0);
                            icon_frame.show(ui, |ui| {
                                ui.label(egui::RichText::new("IA").color(egui::Color32::WHITE).size(20.0).strong());
                            });

                            ui.add_space(15.0);

                            ui.vertical(|ui| {
                                ui.label(egui::RichText::new("Modèle IA Touchless statique").strong().color(egui::Color32::BLACK).size(16.0));
                                ui.label(egui::RichText::new("OpenCV & Pytorch").color(egui::Color32::DARK_GRAY));
                            });

                            ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                                let start_btn = egui::Button::new(egui::RichText::new("Lancer").color(egui::Color32::WHITE))
                                    .fill(dark_blue)
                                    .rounding(15.0)
                                    .min_size(egui::vec2(100.0, 35.0));

                                if ui.add(start_btn).clicked() {
                                    println!("Lancement de la requête API statique");

                                    std::thread::spawn(|| {
                                        let response = reqwest::blocking::get("http://127.0.0.1:8000/static/run");

                                        match response {
                                            Ok(res) => {
                                                if let Ok(body) = res.text() {
                                                    println!("Réponse reçue : {}", body);
                                                }
                                            }
                                            Err(e) => println!("Erreur API : {}", e),
                                        }
                                    });
                                }
                            });
                        });
                    });

                    block_frame.show(ui, |ui| {
                        ui.set_width(ui.available_width());

                        ui.horizontal(|ui| {
                            let icon_frame = egui::Frame::none().fill(egui::Color32::BLACK).rounding(10.0).inner_margin(15.0);
                            icon_frame.show(ui, |ui| {
                                ui.label(egui::RichText::new("IA").color(egui::Color32::WHITE).size(20.0).strong());
                            });

                            ui.add_space(15.0);

                            ui.vertical(|ui| {
                                ui.label(egui::RichText::new("Modèle IA Touchless dynamique").strong().color(egui::Color32::BLACK).size(16.0));
                                ui.label(egui::RichText::new("OpenCV & Pytorch").color(egui::Color32::DARK_GRAY));
                            });

                            ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                                let start_btn = egui::Button::new(egui::RichText::new("Lancer").color(egui::Color32::WHITE))
                                    .fill(dark_blue)
                                    .rounding(15.0)
                                    .min_size(egui::vec2(100.0, 35.0));

                                if ui.add(start_btn).clicked() {
                                    println!("Lancement de la requête API dynamique");

                                    std::thread::spawn(|| {
                                        let response = reqwest::blocking::get("http://127.0.0.1:8000/dynamic/run");

                                        match response {
                                            Ok(res) => {
                                                if let Ok(body) = res.text() {
                                                    println!("Réponse reçue : {}", body);
                                                }
                                            }
                                            Err(e) => println!("Erreur API : {}", e),
                                        }
                                    });
                                }
                            });
                        });
                    });

                    ui.allocate_space(ui.available_size());
                });
            });

            ui.add_space(40.0);

            // --- PARTIE DROITE : Crédits avec LOGO en FOND ---

            // On utilise un Layout::top_down pour empiler l'image puis le texte
            ui.with_layout(egui::Layout::top_down(egui::Align::LEFT), |ui| {

                // 1. AFFICHER LE LOGO EN FILIGRANE
                // On récupère l'espace disponible
                let available_rect = ui.available_rect_before_wrap();

                // On crée une Frame fantôme centriste pour dessiner l'image
                egui::Frame::none().inner_margin(0.0).show(ui, |ui| {
                    // On centre l'image verticalement dans la zone disponible
                    ui.add_space(available_rect.height() * 0.2);


                    let img_width = ui.available_width() * 0.9;
                    ui.add(egui::Image::new(egui::include_image!("../assets/logo.png"))
                        .tint(egui::Color32::from_white_alpha(15)) // Opacité faible (15/255)
                        .max_width(img_width)
                    );
                });

                // 2. AFFICHER LES TEXTES PAR-DESSUS (Rangés en bas)
                ui.with_layout(egui::Layout::bottom_up(egui::Align::LEFT), |ui| {
                    ui.add_space(20.0);
                    ui.label(egui::RichText::new("Université du Québec à Chicoutimi (UQAC) - Hiver 2026").color(egui::Color32::WHITE).strong());
                    ui.add_space(10.0);
                    ui.label(egui::RichText::new("Créé par : Vincent, Yann, Marin, Florian et Clara").color(egui::Color32::LIGHT_GRAY));
                    ui.add_space(30.0);
                });
            });
        });
    });
}