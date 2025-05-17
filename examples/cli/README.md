# gedge

The cli has three major commands:

1. `gedge push`
2. `gedge pull`
3. `gedge push-pull`

Run `gedge -h` and `gedge [subcommand] -h` for more information.
To get the examples in `./examples` working, run these three commands, in this order:

1. `gedge --model-dir "./models" push-pull ./examples/cli/bar.json5`
2. `gedge --model-dir "./models" push-pull ./examples/cli/parent.json5`
3. `gedge --model-dir "./models" push-pull ./examples/cli/qux.json5`
