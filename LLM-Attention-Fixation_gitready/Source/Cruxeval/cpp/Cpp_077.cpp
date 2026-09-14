#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string character) {
    int pos = text.rfind(character);
    if (pos != std::string::npos) {
        std::string subject = text.substr(pos);
        int count = std::count(text.begin(), text.end(), character[0]);
        return subject.append(count-1, character[0]);
    }
    return "";
}
int main() {
    auto candidate = f;
    assert(candidate(("h ,lpvvkohh,u"), ("i")) == (""));
}
