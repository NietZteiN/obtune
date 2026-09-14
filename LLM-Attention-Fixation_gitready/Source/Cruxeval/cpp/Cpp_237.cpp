#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string character) {
    if (text.find(character) != std::string::npos) {
        std::string suff, pref;
        int pos = text.find(character);
        suff = text.substr(0, pos);
        pref = text.substr(pos + character.size());
        std::string tempPref = suff.substr(0, suff.size() - character.size()) + suff.substr(suff.size() - character.size() + 1);
        return suff + character + character + tempPref + pref;
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("uzlwaqiaj"), ("u")) == ("uuzlwaqiaj"));
}
