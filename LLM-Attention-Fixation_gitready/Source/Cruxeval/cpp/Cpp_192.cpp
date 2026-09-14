#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string suffix) {
    std::string output = text;
    while (text.size() >= suffix.size() && text.substr(text.size() - suffix.size()) == suffix) {
        output = text.substr(0, text.size() - suffix.size());
        text = output;
    }
    return output;
}
int main() {
    auto candidate = f;
    assert(candidate(("!klcd!ma:ri"), ("!")) == ("!klcd!ma:ri"));
}
