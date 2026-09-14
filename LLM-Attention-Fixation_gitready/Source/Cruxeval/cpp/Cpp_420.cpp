#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string text) {
    try {
        return std::all_of(text.begin(), text.end(), isalpha);
    } catch(...) {
        return false;
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("x")) == (true));
}
