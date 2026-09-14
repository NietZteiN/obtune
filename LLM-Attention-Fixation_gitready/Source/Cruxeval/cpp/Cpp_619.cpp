#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string title) {
    transform(title.begin(), title.end(), title.begin(), ::tolower);
    return title;
}
int main() {
    auto candidate = f;
    assert(candidate(("   Rock   Paper   SCISSORS  ")) == ("   rock   paper   scissors  "));
}
