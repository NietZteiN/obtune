#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    for (int i = text.size()-1; i > 0; --i) {
        if (!isupper(text[i])) {
            return text.substr(0, i);
        }
    }
    return "";
}
int main() {
    auto candidate = f;
    assert(candidate(("SzHjifnzog")) == ("SzHjifnzo"));
}
