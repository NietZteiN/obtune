#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    for (int i = 0; i < text.length()-1; i++) {
        if (std::all_of(text.begin() + i, text.end(), ::islower)) {
            return text.substr(i + 1);
        }
    }
    return "";
}
int main() {
    auto candidate = f;
    assert(candidate(("wrazugizoernmgzu")) == ("razugizoernmgzu"));
}
