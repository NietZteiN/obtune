#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string text) {
    for (char c : text) {
        if (islower(c)) {
            return false;
        }
    }
    return true;
}
int main() {
    auto candidate = f;
    assert(candidate(("VTBAEPJSLGAHINS")) == (true));
}
