#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string text) {
    for(char ch : text) {
        if(!std::isspace(ch)) {
            return false;
        }
    }
    return true;
}
int main() {
    auto candidate = f;
    assert(candidate(("     i")) == (false));
}
