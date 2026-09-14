#include<assert.h>
#include<bits/stdc++.h>

std::string f(std::tuple<long, long, long, long> tuple_list, std::string joint) {
    std::string string = "";
    auto append_to_string = [&](auto num) {
        std::unordered_map<char, int> dict;
        for (char c : std::to_string(num)) {
            dict[c] = 1;
        }
        string += dict.begin()->first + joint;
    };
    std::apply([&](auto... nums) { (append_to_string(nums), ...); }, tuple_list);
    return string;
}
int main() {
    auto candidate = f;
    assert(candidate((std::make_tuple(32332, 23543, 132323, 33300)), (",")) == ("2,4,2,0,"));
}
