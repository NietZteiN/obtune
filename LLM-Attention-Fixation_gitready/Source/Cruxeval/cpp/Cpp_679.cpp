#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string text) {
    if (text.empty()) {
        return false;
    }
    char first_char = text[0];
    if (isdigit(text[0])) {
        return false;
    }
    for (char last_char : text) {
        if ((last_char != '_') && !isalpha(last_char) && !isdigit(last_char)) {
            return false;
        }
    }
    return true;
}
int main() {
    auto candidate = f;
    assert(candidate(("meet")) == (true));
}
