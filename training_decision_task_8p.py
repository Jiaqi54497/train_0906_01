#Training Simple Decision Making task
import numpy as np
import argparse
import sys
sys.path.insert(0, '../../../') #This line adds '../..' to the path so we can import the net_framework python file
from RNN_model_GRAD import *
import tensorflow as tf
from tensorflow import keras
import json
from tqdm import tqdm
import os
import pickle

def main(args):

    num_iters = args.num_iters
    num_nodes = args.num_nodes
    num_networks = args.num_networks

    for network_number in range(num_networks):
        #Defining Network
        time_constant = 100 #ms
        timestep = 10 #ms
        noise_strength = .01
        num_inputs = 16

        connectivity_matrix = np.ones((num_nodes, num_nodes))
        weight_matrix = np.random.normal(0, 1.2/np.sqrt(num_nodes), (num_nodes, num_nodes))
        for i in range(num_nodes):
            weight_matrix[i,i] = 0
            connectivity_matrix[i,i] = 0
        weight_matrix = tf.Variable(weight_matrix)
        connectivity_matrix = tf.constant(connectivity_matrix)

        # noise_weights = 1 * np.ones(num_nodes)
        # input1_weights = np.random.normal(0, 1/np.sqrt(num_inputs), num_nodes)/2
        # bias_weights = np.random.normal(0, 1/np.sqrt(num_inputs), num_nodes)
        # input2_weights = np.random.normal(0, 1/np.sqrt(num_inputs), num_nodes)/2
        # input3_weights = np.random.normal(0, 1/np.sqrt(num_inputs), num_nodes)/2
        # input4_weights = np.random.normal(0, 1/np.sqrt(num_inputs), num_nodes)/2
        # input5_weights = np.random.normal(0, 1/np.sqrt(num_inputs), num_nodes)/2
        # input6_weights = np.random.normal(0, 1/np.sqrt(num_inputs), num_nodes)/2
        # input7_weights = np.random.normal(0, 1/np.sqrt(num_inputs), num_nodes)/2
        # input8_weights = np.random.normal(0, 1/np.sqrt(num_inputs), num_nodes)/2
        noise_weights = 1 * np.ones(num_nodes)
        bias_weights = np.random.normal(0, 1/np.sqrt(num_inputs), num_nodes)
        def get_inputs(num_nodes,num_inputs):

            input_weight_matrix=np.vstack((bias_weights, noise_weights))
            for i in range(num_inputs):
                input_weight_matrix = np.vstack((input_weight_matrix, np.random.normal(0, 1/np.sqrt(num_inputs), num_nodes)/2))
            return tf.constant(input_weight_matrix)

        input_weight_matrix = get_inputs(num_nodes,num_inputs)
        # input_weight_matrix = tf.constant(np.vstack((bias_weights, noise_weights, input1_weights, input2_weights, input3_weights, input4_weights, input5_weights, input6_weights, input7_weights, input8_weights)))

        def input1(time):
            #No input for now
            return 0

        # def input2(time):
            # return 0
        # def input3(time):
            # return 0
        # def input4(time):
            # return 0
        # def input5(time):
            # return 0
        # def input6(time):
            # return 0
        # def input7(time):
            # return 0
        # def input8(time):
            # return 0

        def bias(time):
            return 1
        def noise(time):
            return np.sqrt(2 * time_constant/timestep) * noise_strength * np.random.normal(0, 1)

        def get_0_input_functs(num_inputs):
            input_funcs = [bias, noise]
            for i in range(num_inputs):
                input_funcs.append(input1)
            return input_funcs

        input_funcs = get_0_input_functs(num_inputs)

        #input_funcs = [bias, noise, input1, input2, input3, input4, input5, input6, input7, input8]
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1Change the number of outputs here.
        init_activations = tf.constant(np.zeros((num_nodes, 8)))
        output_weight_matrix = tf.constant(np.random.uniform(0, 1/np.sqrt(num_nodes), (8, num_nodes)))

        network = RNN(weight_matrix, connectivity_matrix, init_activations, output_weight_matrix, time_constant = time_constant,
                     timestep = timestep, activation_func = keras.activations.relu, output_nonlinearity = lambda x : x)

        #Training Network
        net_weight_history = {}

        time = 15000 #ms
        targets = []
        inputs = []
        error_masks = []

        def error_mask_func(time):
                #Makes loss automatically 0 during switch for 150 ms.
                #Also used in next training section.
            if time < 100:
                return 0
            if time < switch_time + 100 and time > switch_time - 50:
                return 0
            else:
                return 1

        vals = [0.07467629610156967,
                 0.7359636110186749,

                 0.8539031805891266,
                 0.2217757958985292,

                 1.0626550395145082,
                 1.658718091495952,

                 1.5236087579751052,
                 0.6748203691430474,

                 1.503502492405255,
                 0.5515897513164214,

                 0.7399393606650884,
                 1.9693085139963118,

                 1.16170464268611529,
                 0.16254168289490778,

                 1.5630782552283364,
                 0.43710186628152736,

                 1.0336961211169585,
                 1.611615114846882,

                 1.0401701787650914,
                 0.2431485181121429,

                 1.6216936770094201,
                 0.7940338406666316,

                 0.201048287764956,
                 1.1074806890706668,

                 1.7261748017980978,
                 0.5199807105927352,

                 0.6068925081516026,
                 1.0121364798169339,

                 1.7573508638878571,
                 1.154040710372573,

                 0.3567944504236231,
                 1.5390409894022066]

        print('Preprocessing...', flush = True)
        for iter in tqdm(range(num_iters * 5), leave = True, position = 0):
            switch_time = int(np.random.normal(time/2, time/10))
            # input1, input2, input3, input4, input5, input6, input7, input8, target_func_1, target_func_2, target_func_3, target_func_4, error_mask_func = gen_functions()

            def get_target_funcs(num_inputs,switch_time):
                target_funcs = []
                for i in range(num_inputs//2):
                    def target_func(time, i_copy=i):
                        #running for 15 seconds = 15000ms
                        if time < switch_time:
                            return 0.5 * (vals[i_copy] > vals[i_copy+2]) + .8 * (vals[i_copy+2]> vals[i_copy])
                        else:
                            return 0.5 * (vals[i_copy+1] > vals[i_copy+3]) + .8 * (vals[i_copy+3] > vals[i_copy+1])

                    target_funcs.append(target_func)
                return target_funcs

            target_funcs = get_target_funcs(num_inputs,switch_time)
            # targets.append(network.convert(time, [target_func_1,target_func_2,target_func_3,target_func_4]))
            targets.append(network.convert(time, target_funcs))

            def get_input_funcs(num_inputs,vals,time,switch_time):
                for i in range(num_inputs):
                    def input_func(time,i_copy=i):
                        if time < switch_time:
                            return vals[i_copy] + np.random.normal(0, .01)
                        else:
                            return vals[i_copy+1] + np.random.normal(0, .01)

                    input_funcs[i+2] = input_func

                return input_funcs

            input_funcs = get_input_funcs(num_inputs,vals,time,switch_time)

            inputs.append(network.convert(time, input_funcs))
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # error_masks.append(network.convert(time, [error_mask_func,error_mask_func,error_mask_func,error_mask_func]))

            def get_error_mask_funcs(num_inputs):
                error_mask_funcs = []
                for i in range(num_inputs//2):
                    error_mask_funcs.append(error_mask_func)
                return error_mask_funcs

            error_mask_funcs = get_error_mask_funcs(num_inputs)

            error_masks.append(network.convert(time, error_mask_funcs))
        print('Training...', flush = True)
        print('Targets:',len(targets))
        print('Inputs:',len(inputs))

        weight_history, losses = network.train(num_iters, targets, time, num_trials = 10, inputs = inputs,
                      input_weight_matrix = input_weight_matrix, learning_rate = .001, error_mask = error_masks, save = 20)

        net_weight_history['trained weights'] = np.asarray(weight_history).tolist()

        net_weight_history['bias'] = bias_weights.tolist()
        net_weight_history['noise weights'] = noise_weights.tolist()
        net_weight_history['input weights'] = np.asarray(input_weight_matrix).tolist()
        # net_weight_history['input2 weights'] = input2_weights.tolist()
        net_weight_history['connectivity matrix'] = np.asarray(connectivity_matrix).tolist()
        net_weight_history['output weights'] = np.asarray(output_weight_matrix).tolist()

        if not os.path.isdir(args.savedir):
            os.mkdir(args.savedir)

        network_params = {}
        network_params['n_nodes'] = num_nodes
        network_params['time_constant'] = time_constant
        network_params['timestep'] = timestep
        network_params['noise_strength'] = noise_strength
        network_params['num_input'] = num_inputs

        with open('%s/network_params.dat' % args.savedir, 'wb') as f:
            f.write(pickle.dumps(network_params))

        if not os.path.isdir('%s/weight_history_' % args.savedir):
            os.mkdir('%s/weight_history_' % args.savedir)

        with open('%s/weight_history_' % args.savedir + str(network_number)+'.json', 'w') as f:
            json.dump(net_weight_history, f)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('savedir')
    parser.add_argument('--num_iters', type=int, default=1000)
    parser.add_argument('--num_nodes', type=int, default=256)
    parser.add_argument('--num_networks', type=int, default=1)

    args = parser.parse_args()
    main(args)
