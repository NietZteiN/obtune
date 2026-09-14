#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string characters) {
    std::vector<char> character_list(characters.begin(), characters.end());
    character_list.push_back(' ');
    character_list.push_back('_');

    int i = 0;
    while (i < text.length() && std::find(character_list.begin(), character_list.end(), text[i]) != character_list.end()) {
        i++;
    }

    return text.substr(i);
}
int main() {
    auto candidate = f;
    assert(candidate(("2nm_28in"), ("nm")) == ("2nm_28in"));
}
