#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string use) {
    size_t pos = text.find(use);
    while (pos != std::string::npos) {
        text.replace(pos, use.length(), "");
        pos = text.find(use, pos);
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("Chris requires a ride to the airport on Friday."), ("a")) == ("Chris requires  ride to the irport on Fridy."));
}
