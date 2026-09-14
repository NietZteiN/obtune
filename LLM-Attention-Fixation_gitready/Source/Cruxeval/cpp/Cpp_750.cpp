#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::map<std::string,std::string> char_map, std::string text) {
    std::string new_text = "";
    for (char ch : text) {
        auto it = char_map.find(std::string(1, ch));
        if (it == char_map.end()) {
            new_text += ch;
        } else {
            new_text += it->second;
        }
    }
    return new_text;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,std::string>()), ("hbd")) == ("hbd"));
}
