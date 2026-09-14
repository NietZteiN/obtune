#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string values, std::string text, std::string markers) {
    size_t pos = text.find_last_not_of(values);
    if (pos != std::string::npos) {
        text.erase(pos + 1);
    }

    pos = text.find_last_not_of(markers);
    if (pos != std::string::npos) {
        text.erase(pos + 1);
    }

    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("2Pn"), ("yCxpg2C2Pny2"), ("")) == ("yCxpg2C2Pny"));
}
