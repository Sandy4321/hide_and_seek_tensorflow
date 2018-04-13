import tensorflow as tf
from config import *
from network import *


def train(args, sess, model):
    #optimizers
    optimizer = tf.train.AdamOptimizer(args.learning_rate, beta1=args.momentum, name="AdamOptimizer").minimize(model.loss, var_list=model.vars)

    start_epoch = 0
    step = 0
    global_step = 0

    #saver
    saver = tf.train.Saver()        
    if args.continue_training:
        last_ckpt = tf.train.latest_checkpoint(args.checkpoints_path)
        saver.restore(sess, last_ckpt)
        ckpt_name = str(last_ckpt)
        print("Loaded model file from " + ckpt_name)
        ckpt_numbers = ckpt_name.split('-')
        start_epoch = int(ckpt_numbers[-2])
        step = global_step = int(ckpt_numbers[-1])
        tf.local_variables_initializer().run()
    else:
        tf.global_variables_initializer().run()
        tf.local_variables_initializer().run()


    #summary init
    all_summary = tf.summary.merge([model.loss_sum,
                                    model.tr_acc_sum, 
                                    model.val_acc_sum,
                                    model.train_img_sum,
                                    model.tr_classmap_sum,
                                    model.val_img_sum,
                                    model.val_classmap_sum,
                                    ])
    writer = tf.summary.FileWriter(args.graph_path, sess.graph)


    #Prepare data
    #prepare training data
    train_imgs, train_boxes, train_labels, labels_dict, train_count = load_tr_data(args) 
    valid_imgs, valid_boxes, valid_labels, valid_count = load_val_data(args, labels_dict)    

    zipped_data = zip(train_imgs, train_boxes, train_labels)
    np.random.shuffle(zipped_data)
    
    new_imgs, new_boxes, new_labels = [], [], []
    for img, box, label in zipped_data:
        new_imgs.append(img)
        new_boxes.append(box)
        new_labels.append(label)
    train_imgs = np.asarray(new_imgs)
    train_boxes = np.asarray(new_boxes)
    train_labels = np.asarray(new_labels)


    zipped_data = zip(valid_imgs, valid_boxes, valid_labels)
    np.random.shuffle(zipped_data)

    new_imgs, new_boxes, new_labels = [], [], []
    for img, box, label in zipped_data:
        new_imgs.append(img)
        new_boxes.append(box)
        new_labels.append(label)
    valid_imgs = np.asarray(new_imgs)
    valid_boxes = np.asarray(new_boxes)
    valid_labels = np.asarray(new_labels)


    print("Training Count: %d Class Num: %d "%(train_count, train_labels.max()+1))
    
    batch_idxs = train_count // args.batch_size
    #training starts here
    for epoch in range(start_epoch, args.epochs):
        for idx in range(0, batch_idxs):
            tr_img_batch = train_imgs[args.batch_size*idx:args.batch_size*idx+args.batch_size]
            tr_lab_batch = train_labels[args.batch_size*idx:args.batch_size*idx+args.batch_size]
            tr_box_batch = train_boxes[args.batch_size*idx:args.batch_size*idx+args.batch_size]

            val_img_batch = valid_imgs[args.batch_size*idx:args.batch_size*idx+args.batch_size]
            val_lab_batch = valid_labels[args.batch_size*idx:args.batch_size*idx+args.batch_size]
            val_box_batch = valid_boxes[args.batch_size*idx:args.batch_size*idx+args.batch_size]

            tr_batch = [load_image(path, args, is_training=True) for path in tr_img_batch]
            val_batch = [load_image(path, args, is_training=False) for path in val_img_batch]
            tr_batch = np.asarray(tr_batch)
            val_batch = np.asarray(val_batch)

            if len(tr_img_batch) < args.batch_size or len(val_img_batch) < args.batch_size:
                break
            #Update Network
            summary, loss, acc, val_acc, _ = sess.run([all_summary, model.loss, model.acc, model.val_acc, optimizer],
                                                       feed_dict={model.train_imgs:tr_batch,
                                                                  model.train_labels:tr_lab_batch,
                                                                  model.val_imgs:val_batch,
                                                                  model.val_labels:val_lab_batch
                                                                  }
                                                      )
            writer.add_summary(summary, global_step)



            print("Epoch [%d] Step [%d] Loss: [%.4f] Acc: [%.4f] Val: [%.4f]" % (epoch, step, loss, acc, val_acc))
            
            if global_step%args.checkout_point == 0:
                saver.save(sess, args.checkpoints_path + "/model-"+str(epoch), global_step=step)
                print("Model saved at /model-" + str(epoch) + "-" + str(step))
                

            if step*args.batch_size > train_count:
                epoch += 1 
                step = 0
                saver.save(sess, args.checkpoints_path + "/model-"+str(epoch), global_step=step)
                print("Model saved at /model-" + str(epoch) + "-" + str(step))
                
            step += 1
            global_step += 1

        #update learning rate after every epoch


      
    print("Done.")


def main(_):
    run_config = tf.ConfigProto()
    run_config.gpu_options.allow_growth = True
    
    with tf.Session(config=run_config) as sess:
        model = network(args)

        print('Start Training...')
        train(args, sess, model)

main(args)

#Still Working....