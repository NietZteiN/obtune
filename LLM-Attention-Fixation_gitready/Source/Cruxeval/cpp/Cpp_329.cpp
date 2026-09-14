#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string text) {
    for (int i = 1; i < text.length(); i++) {
        if (text[i] == toupper(text[i]) && islower(text[i-1])) {
            return true;
        }
    }
    return false;
}
int main() {
    auto candidate = f;
    assert(candidate(("jh54kkk6")) == (true));
}
