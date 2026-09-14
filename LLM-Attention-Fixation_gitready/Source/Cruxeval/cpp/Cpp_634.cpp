#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string input_string) {
    std::string table = "aioe";
    std::string replace = "ioua";
    std::map<char, char> translation;
    for (int i = 0; i < table.length(); ++i) {
        translation[table[i]] = replace[i];
    }

    while (input_string.find_first_of("aA") != std::string::npos) {
        for (int i = 0; i < input_string.length(); ++i) {
            if (translation.find(input_string[i]) != translation.end()) {
                input_string[i] = translation[input_string[i]];
            }
        }
    }
    
    return input_string;
}
int main() {
    auto candidate = f;
    assert(candidate(("biec")) == ("biec"));
}
