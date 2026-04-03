use eframe::egui;
use crate::views::{home, settings};

#[derive(PartialEq)]
pub enum View {
    Home,
    Settings,
}

pub struct TouchlessApp {
    current_view: View,
}

impl Default for TouchlessApp {
    fn default() -> Self {
        Self { current_view: View::Home }
    }
}

impl eframe::App for TouchlessApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        // On passe `ctx` au lieu de `ui` pour que chaque page gère son propre fond
        match self.current_view {
            View::Home => home::show(ctx, &mut self.current_view),
            View::Settings => settings::show(ctx, &mut self.current_view),
        }
    }
}