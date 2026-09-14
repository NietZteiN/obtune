#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string chars) {
    std::vector<char> chars_vec(chars.begin(), chars.end());
    std::vector<char> text_vec(text.begin(), text.end());
    std::vector<char> new_text = text_vec;
    
    while (new_text.size() > 0 && text_vec.size() > 0) {
        if (std::find(chars_vec.begin(), chars_vec.end(), new_text[0]) != chars_vec.end()) {
            new_text.erase(new_text.begin());
        } else {
            break;
        }
    }

    return std::string(new_text.begin(), new_text.end());
}
int main() {
    auto candidate = f;
    assert(candidate(("asfdellos"), ("Ta")) == ("sfdellos"));
}
