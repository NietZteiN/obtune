#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string item) {
    std::string modified = item;
    size_t pos = modified.find(". ");
    while (pos != std::string::npos) {
        modified.replace(pos, 2, " , ");
        pos = modified.find(". ", pos + 1);
    }
    pos = modified.find("&#33; ");
    while (pos != std::string::npos) {
        modified.replace(pos, 5, "! ");
        pos = modified.find("&#33; ", pos + 1);
    }
    pos = modified.find(". ");
    while (pos != std::string::npos) {
        modified.replace(pos, 2, "? ");
        pos = modified.find(". ", pos + 1);
    }
    pos = modified.find(". ");
    while (pos != std::string::npos) {
        modified.replace(pos, 2, ". ");
        pos = modified.find(". ", pos + 1);
    }
    modified[0] = std::toupper(modified[0]);
    return modified;
}
int main() {
    auto candidate = f;
    assert(candidate((".,,,,,. منبت")) == (".,,,,, , منبت"));
}
