use eframe::egui;
use crate::views::{home, settings};
use std::sync::mpsc::{Receiver, Sender, channel};

#[derive(PartialEq)]
pub enum View {
    Home,
    Settings,
}

// Structure pour suivre l'état de chaque geste
pub struct GestureState {
    pub name: String,
    pub is_modified: bool,
    pub category: String,
}

pub struct TouchlessApp {
    pub current_view: View,
    // On stocke l'état de modification de la popup ici
    pub edit_state: settings::EditState,
    // On stocke la liste des gestes pour garder en mémoire ceux modifiés
    pub gestures: Vec<GestureState>,
    pub tx: Sender<String>,       // Pour envoyer le nom du geste réussi
    pub rx: Receiver<String>,     // Pour recevoir le nom dans l'UI
}

impl Default for TouchlessApp {
    fn default() -> Self {
        let (tx, rx) = channel(); // On crée le canal
        Self {
            current_view: View::Home,
            edit_state: settings::EditState::default(),
            gestures: vec![
                GestureState { name: "Move".into(), is_modified: false, category: "Statique".into() },
                GestureState { name: "Grab".into(), is_modified: false, category: "Statique".into() },
                GestureState { name: "Click".into(), is_modified: false, category: "Statique".into() },
                GestureState { name: "Swipe".into(), is_modified: false, category: "Dynamique".into() },
                GestureState { name: "Zoom".into(), is_modified: false, category: "Dynamique".into() },
                GestureState { name: "Question".into(), is_modified: false, category: "Dynamique".into() },
            ],
            tx,
            rx,
        }
    }
}

impl eframe::App for TouchlessApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        // On vérifie si le thread nous a envoyé une confirmation
        while let Ok(gesture_name) = self.rx.try_recv() {
            if let Some(g) = self.gestures.iter_mut().find(|g| g.name == gesture_name) {
                g.is_modified = true;
            }
        }

        match self.current_view {
            View::Home => home::show(ctx, &mut self.current_view),
            // On passe maintenant l'émetteur (tx) à la vue settings
            View::Settings => settings::show(ctx, &mut self.current_view, &mut self.edit_state, &mut self.gestures, self.tx.clone()),
        }
    }
}