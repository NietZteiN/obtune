#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string new_text = text;
    for (int i = 0; i < new_text.length(); i++) {
        char character = new_text[i];
        char new_character = std::islower(character) ? std::toupper(character) : std::tolower(character);
        new_text[i] = new_character;
    }
    return new_text;
}
int main() {
    auto candidate = f;
    assert(candidate(("dst vavf n dmv dfvm gamcu dgcvb.")) == ("DST VAVF N DMV DFVM GAMCU DGCVB."));
}
