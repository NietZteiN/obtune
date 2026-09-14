#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string new_text = "";
    for (char ch : text) {
        if (std::isdigit(ch) || ch == 'Ä' || ch == 'ä' || ch == 'Ï' || ch == 'ï' || ch == 'Ö' || ch == 'ö' || ch == 'Ü' || ch == 'ü') {
            new_text += ch;
        }
    }
    return new_text;
}
int main() {
    auto candidate = f;
    assert(candidate(("")) == (""));
}
