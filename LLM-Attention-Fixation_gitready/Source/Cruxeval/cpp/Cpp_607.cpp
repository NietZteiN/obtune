#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string text) {
    std::vector<char> endings = {'.', '!', '?'};
    for (char i : endings) {
        if (text.back() == i) {
            return true;
        }
    }
    return false;
}
int main() {
    auto candidate = f;
    assert(candidate((". C.")) == (true));
}
