#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string value) {
    std::vector<int> indexes;
    for (int i = 0; i < text.size(); i++) {
        if (text[i] == value[0]) {
            indexes.push_back(i);
        }
    }
    
    std::string new_text = text;
    for (int i = indexes.size() - 1; i >= 0; i--) {
        new_text.erase(indexes[i], 1);
    }
    
    return new_text;
}
int main() {
    auto candidate = f;
    assert(candidate(("scedvtvotkwqfoqn"), ("o")) == ("scedvtvtkwqfqn"));
}
