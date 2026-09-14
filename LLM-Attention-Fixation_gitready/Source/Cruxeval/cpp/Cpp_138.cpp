#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string chars) {
    std::vector<char> listchars(chars.begin(), chars.end());
    char first = listchars.back();
    listchars.pop_back();
    for (char i : listchars) {
        text = text.substr(0, text.find(i)) + i + text.substr(text.find(i) + 1);
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("tflb omn rtt"), ("m")) == ("tflb omn rtt"));
}
