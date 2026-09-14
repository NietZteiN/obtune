#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string result;
    for (int i = 0; i < text.length(); i++) {
        if (!std::isdigit(text[i])) {
            result += text[i];
        }
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("seiq7229 d27")) == ("seiq d"));
}
