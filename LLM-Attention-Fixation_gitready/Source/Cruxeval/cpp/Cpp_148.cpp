#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string forest, std::string animal) {
    size_t index = forest.find(animal);
    std::string result = forest;
    while (index < forest.size() - 1) {
        result[index] = forest[index + 1];
        index++;
    }
    if (index == forest.size() - 1) {
        result[index] = '-';
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("2imo 12 tfiqr."), ("m")) == ("2io 12 tfiqr.-"));
}
