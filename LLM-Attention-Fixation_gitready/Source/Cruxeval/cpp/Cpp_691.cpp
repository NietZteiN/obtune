#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string suffix) {
    if (!suffix.empty() && std::find(text.rbegin(), text.rend(), suffix.back()) != text.rend()) {
        char last_char = suffix.back();
        while (!text.empty() && text.back() == last_char) {
            text.pop_back();
        }
        suffix.pop_back();
        return f(text, suffix);
    } else {
        return text;
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("rpyttc"), ("cyt")) == ("rpytt"));
}
