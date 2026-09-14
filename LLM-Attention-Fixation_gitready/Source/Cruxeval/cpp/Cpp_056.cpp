#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string sentence) {
    for(char c : sentence) {
        if (!isascii(c)) {
            return false;
        }
    }
    return true;
}
int main() {
    auto candidate = f;
    assert(candidate(("1z1z1")) == (true));
}
