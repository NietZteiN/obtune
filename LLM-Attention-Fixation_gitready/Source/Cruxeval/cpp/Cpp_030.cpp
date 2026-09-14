#include<assert.h>
#include<bits/stdc++.h>
#include<variant>

typedef std::variant<std::string, long> Union_std_string_long;

std::vector<Union_std_string_long> f(std::vector<Union_std_string_long> array) {
    std::vector<Union_std_string_long> result;
    for (auto const& elem : array) {
        std::visit([&](auto&& arg) {
            using T = std::decay_t<decltype(arg)>;
            if constexpr (std::is_same_v<T, long>) {
                result.push_back(arg);
            } else if constexpr (std::is_same_v<T, std::string>) {
                std::locale loc;
                if (std::all_of(arg.begin(), arg.end(),
                                [&loc](char c){ return std::isprint(c, loc); })) {
                    result.push_back(arg);
                }
            }
        }, elem);
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<Union_std_string_long>({(std::string)"a", (std::string)"b", (std::string)"c"}))) == (std::vector<Union_std_string_long>({(std::string)"a", (std::string)"b", (std::string)"c"})));
}
