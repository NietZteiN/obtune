#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    for(int i = 10; i > 0; i--) {
        while(text.find(std::to_string(i)) == 0) {
            text = text.substr(1);
        }
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("25000   $")) == ("5000   $"));
}
