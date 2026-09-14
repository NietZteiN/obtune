#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::string text, std::string elem) {
    if (elem != "") {
        while (text.find(elem) == 0) {
            text = text.replace(text.find(elem), elem.length(), "");
        }
        while (elem.find(text) == 0) {
            elem = elem.replace(elem.find(text), text.length(), "");
        }
    }
    return {elem, text};
}
int main() {
    auto candidate = f;
    assert(candidate(("some"), ("1")) == (std::vector<std::string>({(std::string)"1", (std::string)"some"})));
}
