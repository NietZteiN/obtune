#include <assert.h>
#include <bits/stdc++.h>

std::string remove_prefix(std::string &str, const std::string &prefix) {
    if (str.substr(0, prefix.size()) == prefix) {
        return str.substr(prefix.size());
    }
    return str;
}

std::string f(std::string text) {
    for (std::string p : {"acs", "asp", "scn"}) {
        text = remove_prefix(text, p) + ' ';
    }
    return text.substr(0, text.size() - 1);
}
int main() {
    auto candidate = f;
    assert(candidate(("ilfdoirwirmtoibsac")) == ("ilfdoirwirmtoibsac  "));
}
