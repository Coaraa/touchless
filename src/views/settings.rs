use eframe::egui;
use crate::app::{View, GestureState}; // Import de GestureState
use serde::Deserialize;

#[derive(Deserialize)]
struct ApiResponse {
    status: String,
    message: String,
}

#[derive(Default)]
pub struct EditState {
    pub open: bool,
    pub gesture_name: String,
    pub category: String,
}

fn get_emoji(name: &str) -> &str {
    match name {
        "Move" => "✋",
        "Grab" => "✊",
        "Click" => "👆",
        "Swipe" => "👋",
        "Zoom" => "👋",
        "Question" => "👆",
        _ => "❓",
    }
}

pub fn show(ctx: &egui::Context, current_view: &mut View, edit_state: &mut EditState, gestures: &mut Vec<GestureState>, tx: std::sync::mpsc::Sender<String>, is_training: &mut bool) {
    let dark_bg = egui::Color32::from_rgb(26, 34, 44);
    let card_white = egui::Color32::from_rgb(248, 249, 250);
    let accent_dark = egui::Color32::from_rgb(33, 41, 54);
    let circle_blue = egui::Color32::from_rgb(210, 230, 255);
    let modified_gold = egui::Color32::from_rgb(255, 215, 0);

    // --- FENÊTRE POP-UP DE MODIFICATION ---
    if edit_state.open {
        egui::Window::new(format!("Modifier : {}", edit_state.gesture_name))
            .collapsible(false)
            .resizable(false)
            .anchor(egui::Align2::CENTER_CENTER, egui::vec2(0.0, 0.0))
            .show(ctx, |ui| {
                ui.vertical_centered(|ui| {
                    ui.label(format!("Catégorie : {}", edit_state.category));
                    ui.add_space(10.0);

                    if ui.button("Capturer").clicked() {
                        let gesture_to_edit = edit_state.gesture_name.clone();
                        let cat_for_thread = if edit_state.category.to_lowercase() == "statique" { "static" } else { "dynamic" }.to_string();

                        let tx_thread = tx.clone(); // On clone l'émetteur pour le thread

                        std::thread::spawn(move || {
                            // 1. On crée un client capable d'attendre 5 minutes
                            let client = reqwest::blocking::Client::builder()
                                .timeout(std::time::Duration::from_secs(300))
                                .build();
                            let url = format!("http://127.0.0.1:8000/{}/capture/{}", cat_for_thread, gesture_to_edit);

                            match client {
                                Ok(c) => {
                                    // 2. On utilise ce client spécifique au lieu du 'get' par défaut
                                    match c.get(url).send() {
                                        Ok(res) if res.status().is_success() => {
                                            if let Ok(api_res) = res.json::<ApiResponse>() {
                                                if api_res.status == "success" {
                                                    println!("API Succès : {}", api_res.message);
                                                    let _ = tx_thread.send(gesture_to_edit);
                                                } else {
                                                    println!("API Erreur logique : {}", api_res.message);
                                                }
                                            } else {
                                                println!("Erreur : Le JSON de l'API est invalide");
                                            }
                                        }
                                        Ok(res) => println!("Le serveur a répondu avec une erreur : {}", res.status()),
                                        Err(e) => {
                                            if e.is_timeout() {
                                                println!("ERREUR : Timeout de 5 minutes atteint !");
                                            } else {
                                                println!("ERREUR RÉSEAU : {:?}", e);
                                            }
                                        }
                                    }
                                }
                                Err(_) => println!("Impossible de créer le client HTTP"),
                            }
                        });
                        edit_state.open = false;
                    }
                    if ui.button("Réinitialiser").clicked() {
                        let gesture_to_reset = edit_state.gesture_name.clone();
                        let tx_thread = tx.clone(); // On utilise ton canal existant

                        // Déterminer la catégorie (statique ou dynamique)
                        let category = if edit_state.category.to_lowercase() == "statique" { "static" } else { "dynamic" };

                        std::thread::spawn(move || {
                            let url = format!("http://127.0.0.1:8000/{}/reinitialiser/{}", category, gesture_to_reset);

                            if let Ok(response) = reqwest::blocking::get(&url) {
                                if response.status().is_success() {
                                    if let Ok(api_res) = response.json::<ApiResponse>() {
                                        if api_res.status == "success" {
                                            println!("API Succès : {}", api_res.message);
                                            let _ = tx_thread.send(format!("RESET:{}", gesture_to_reset));
                                        } else {
                                            println!("API Erreur logique : {}", api_res.message);
                                        }
                                    } else {
                                        println!("Erreur : Le JSON de l'API est invalide");
                                    }
                                }
                            }
                        });

                        edit_state.open = false;
                    }

                    if ui.add(egui::Button::new("Annuler").frame(false)).clicked() {
                        edit_state.open = false;
                    }
                });
            });
    }

    let block_frame = egui::Frame::none()
        .fill(egui::Color32::from_rgb(240, 242, 245))
        .rounding(15.0)
        .inner_margin(20.0);

    egui::CentralPanel::default().frame(egui::Frame::none().fill(dark_bg)).show(ctx, |ui| {
        egui::Frame::none().inner_margin(20.0).show(ui, |ui| {
            egui::Frame::none().fill(card_white).rounding(20.0).inner_margin(30.0).show(ui, |ui| {
                ui.set_min_size(ui.available_size());

                ui.horizontal(|ui| {
                    let back_btn = egui::Button::new(egui::RichText::new("⬅ Retour").color(accent_dark).size(16.0)).frame(false);
                    if ui.add(back_btn).clicked() { *current_view = View::Home; }
                });

                ui.vertical_centered(|ui| {
                    ui.heading(egui::RichText::new("Configuration des gestes").strong().size(28.0));
                    ui.add_space(30.0);

                    ui.columns(2, |cols| {
                        // --- SECTION STATIQUE ---
                        block_frame.show(&mut cols[0], |ui| {
                            ui.set_min_height(250.0);
                            ui.vertical_centered(|ui| {
                                ui.label(egui::RichText::new("Modèles Statiques").size(18.0).strong().color(accent_dark));
                                ui.add_space(20.0);

                                let static_gestures: Vec<&GestureState> = gestures.iter().filter(|g| g.category == "Statique").collect();
                                ui.columns(3, |sub| {
                                    for (i, gesture) in static_gestures.iter().enumerate() {
                                        draw_gesture_item(&mut sub[i], get_emoji(&gesture.name), &gesture.name, circle_blue, accent_dark, modified_gold, gesture.is_modified, edit_state, "Statique");
                                    }
                                });
                            });
                        });

                        // --- SECTION DYNAMIQUE ---
                        block_frame.show(&mut cols[1], |ui| {
                            ui.set_min_height(250.0);
                            ui.vertical_centered(|ui| {
                                ui.label(egui::RichText::new("Modèles Dynamiques").size(18.0).strong().color(accent_dark));
                                ui.add_space(20.0);

                                let dynamic_gestures: Vec<&GestureState> = gestures.iter().filter(|g| g.category == "Dynamique").collect();
                                ui.columns(3, |sub| {
                                    for (i, gesture) in dynamic_gestures.iter().enumerate() {
                                        draw_gesture_item(&mut sub[i], get_emoji(&gesture.name), &gesture.name, circle_blue, accent_dark, modified_gold, gesture.is_modified, edit_state, "Dynamique");
                                    }
                                });
                            });
                        });
                    });

                    ui.with_layout(egui::Layout::bottom_up(egui::Align::Center), |ui| {
                        ui.add_space(10.0);

                        // Vérification des changements
                        let has_static_changes = gestures.iter().any(|g| (g.category == "Statique" || g.category == "Static") && g.is_modified);
                        let has_dynamic_changes = gestures.iter().any(|g| (g.category == "Dynamique" || g.category == "Dynamic") && g.is_modified);

                        let can_train = (has_static_changes || has_dynamic_changes) && !*is_training;

                        let btn_text = if *is_training {
                            "Entraînement en cours..."
                        } else if !can_train {
                            "Rien à entraîner"
                        } else {
                            "Démarrer l'entraînement"
                        };

                        let btn = egui::Button::new(egui::RichText::new(btn_text).color(egui::Color32::WHITE).size(18.0))
                            .min_size(egui::vec2(300.0, 50.0))
                            .rounding(25.0)
                            .fill(if can_train { accent_dark } else { egui::Color32::GRAY });

                        if ui.add_enabled(can_train, btn).clicked() {
                            *is_training = true;

                            if has_static_changes {
                                let tx_thread = tx.clone();
                                std::thread::spawn(move || {
                                    let url = "http://127.0.0.1:8000/static/train";

                                    // 1. On tente la requête
                                    if let Ok(response) = reqwest::blocking::get(url) {
                                        // 2. On vérifie le code HTTP et on tente de lire le JSON
                                        if response.status().is_success() {
                                            if let Ok(api_res) = response.json::<ApiResponse>() {
                                                if api_res.status == "success" {
                                                    println!("Succès API : {}", api_res.message);
                                                    // On n'envoie le signal que si TOUT est OK
                                                    let _ = tx_thread.send("TRAINING_DONE".to_string());
                                                    return; // On sort proprement
                                                }
                                            }
                                        }
                                    }
                                });
                            }
                            if has_dynamic_changes {
                                let tx_thread = tx.clone();
                                std::thread::spawn(move || {
                                    let url = "http://127.0.0.1:8000/dynamic/train";

                                    // 1. On tente la requête
                                    if let Ok(response) = reqwest::blocking::get(url) {
                                        // 2. On vérifie le code HTTP et on tente de lire le JSON
                                        if response.status().is_success() {
                                            if let Ok(api_res) = response.json::<ApiResponse>() {
                                                if api_res.status == "success" {
                                                    println!("Succès API : {}", api_res.message);
                                                    // On n'envoie le signal que si TOUT est OK
                                                    let _ = tx_thread.send("TRAINING_DONE".to_string());
                                                    return; // On sort proprement
                                                }
                                            }
                                        }
                                    }
                                });
                            }
                        }

                        if *is_training {
                            ui.add_space(10.0);
                            ui.horizontal(|ui| {
                                ui.spinner();
                                ui.label("L'IA analyse vos gestes...");
                            });
                        }
                    });
                });
            });
        });
    });
}

fn draw_gesture_item(ui: &mut egui::Ui, emoji: &str, name: &str, circle_col: egui::Color32, accent_dark: egui::Color32, border_col: egui::Color32, is_modified: bool, edit_state: &mut EditState, category: &str) {
    ui.vertical_centered(|ui| {
        let mut btn = egui::Button::new(egui::RichText::new(emoji).size(30.0)).min_size(egui::vec2(70.0, 70.0)).rounding(35.0).fill(circle_col);
        if is_modified { btn = btn.stroke(egui::Stroke::new(2.5, border_col)); }
        if ui.add(btn).clicked() {
            if category == "Statique" {
                edit_state.open = true;
            }
            edit_state.gesture_name = name.to_string();
            edit_state.category = category.to_string();
        }
        ui.add_space(8.0);
        let label_fill = if is_modified { border_col } else { accent_dark };
        let label = egui::Button::new(egui::RichText::new(name).size(12.0).color(egui::Color32::WHITE)).min_size(egui::vec2(70.0, 22.0)).rounding(20.0).fill(label_fill);
        if ui.add(label).clicked() {
            if category == "Statique" {
                edit_state.open = true;
            }
            edit_state.open = true;
            edit_state.gesture_name = name.to_string();
            edit_state.category = category.to_string();
        }
    });
}